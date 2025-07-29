"""
Comprehensive distributed processing tests.

Copyright (c) 2025 Alban Maxhuni <alban.q.maxhuni@gmail.com>

This software is dual-licensed under AGPL-3.0 (open-source) and Commercial licenses.
For commercial licensing, contact: alban.q.maxhuni@gmail.com
"""

import pytest
import asyncio
import time
import numpy as np
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from typing import List, Dict, Any
import json

from ai_prishtina_milvus_client.distributed import (
    DistributedProcessor,
    DistributedConfig,
    WorkerNode,
    TaskResult,
    TaskStatus,
    LoadBalancer,
    TaskQueue,
    CoordinatorNode
)
from ai_prishtina_milvus_client.config import MilvusConfig
from ai_prishtina_milvus_client.exceptions import DistributedError


class TestDistributedProcessorComprehensive:
    """Comprehensive distributed processor tests."""

    @pytest.fixture
    def distributed_config(self):
        """Create distributed configuration."""
        return DistributedConfig(
            coordinator_host="localhost",
            coordinator_port=8080,
            worker_count=4,
            task_queue_size=1000,
            heartbeat_interval=5.0,
            task_timeout=30.0,
            max_retries=3,
            load_balancing_strategy="round_robin",
            enable_auto_scaling=True,
            min_workers=2,
            max_workers=8
        )

    @pytest.fixture
    def milvus_config(self):
        """Create Milvus configuration."""
        return MilvusConfig(
            host="localhost",
            port=19530,
            collection_name="test_collection",
            dim=128
        )

    @pytest.mark.asyncio
    async def test_distributed_search_workflow(self, distributed_config, milvus_config):
        """Test complete distributed search workflow."""
        with patch('ai_prishtina_milvus_client.distributed.WorkerNode') as mock_worker_class, \
             patch('ai_prishtina_milvus_client.distributed.CoordinatorNode') as mock_coordinator_class:
            
            # Mock coordinator
            mock_coordinator = AsyncMock()
            mock_coordinator.start.return_value = None
            mock_coordinator.register_worker.return_value = True
            mock_coordinator_class.return_value = mock_coordinator
            
            # Mock workers
            mock_workers = []
            for i in range(distributed_config.worker_count):
                worker = AsyncMock()
                worker.worker_id = f"worker_{i}"
                worker.is_active = True
                worker.process_task.return_value = TaskResult(
                    task_id=f"task_{i}",
                    status=TaskStatus.COMPLETED,
                    worker_id=f"worker_{i}",
                    result=[{"id": j, "distance": 0.1 * j} for j in range(10)],
                    processing_time=0.5,
                    metadata={"batch_size": 10}
                )
                mock_workers.append(worker)
            
            mock_worker_class.side_effect = mock_workers
            
            processor = DistributedProcessor(
                distributed_config=distributed_config,
                milvus_config=milvus_config
            )
            
            await processor.start()
            
            # Test distributed search
            query_vectors = [np.random.rand(128).tolist() for _ in range(100)]
            
            start_time = time.time()
            results = await processor.distributed_search(
                query_vectors=query_vectors,
                top_k=10,
                search_params={"nprobe": 16}
            )
            processing_time = time.time() - start_time
            
            # Verify results
            assert len(results) == 100  # One result per query vector
            
            # Verify all workers were utilized
            for worker in mock_workers:
                worker.process_task.assert_called()
            
            # Verify performance improvement from distribution
            assert processing_time < 10.0  # Should be much faster than sequential
            
            # Get processing statistics
            stats = await processor.get_processing_statistics()
            assert stats["total_tasks_processed"] == 100
            assert stats["active_workers"] == distributed_config.worker_count
            assert stats["average_task_time"] > 0

    @pytest.mark.asyncio
    async def test_load_balancing_strategies(self, distributed_config, milvus_config):
        """Test different load balancing strategies."""
        strategies = ["round_robin", "least_loaded", "random", "weighted"]
        
        for strategy in strategies:
            config = distributed_config.copy()
            config.load_balancing_strategy = strategy
            
            with patch('ai_prishtina_milvus_client.distributed.WorkerNode') as mock_worker_class:
                
                # Mock workers with different loads
                mock_workers = []
                for i in range(4):
                    worker = AsyncMock()
                    worker.worker_id = f"worker_{i}"
                    worker.is_active = True
                    worker.current_load = i * 0.25  # Different load levels
                    worker.process_task.return_value = TaskResult(
                        task_id=f"task_{i}",
                        status=TaskStatus.COMPLETED,
                        worker_id=f"worker_{i}",
                        result={"processed": True},
                        processing_time=0.1
                    )
                    mock_workers.append(worker)
                
                mock_worker_class.side_effect = mock_workers
                
                processor = DistributedProcessor(
                    distributed_config=config,
                    milvus_config=milvus_config
                )
                
                await processor.start()
                
                # Test load balancing
                tasks = [{"task_id": f"task_{i}", "data": f"data_{i}"} for i in range(20)]
                
                results = await processor.process_tasks_batch(tasks)
                
                # Verify all tasks were processed
                assert len(results) == 20
                assert all(r.status == TaskStatus.COMPLETED for r in results)
                
                # Verify load balancing behavior
                load_balancer_stats = await processor.get_load_balancer_statistics()
                assert load_balancer_stats["strategy"] == strategy
                assert load_balancer_stats["total_tasks_distributed"] == 20
                
                await processor.stop()

    @pytest.mark.asyncio
    async def test_fault_tolerance_and_recovery(self, distributed_config, milvus_config):
        """Test fault tolerance and recovery mechanisms."""
        with patch('ai_prishtina_milvus_client.distributed.WorkerNode') as mock_worker_class:
            
            # Mock workers - some will fail
            mock_workers = []
            for i in range(4):
                worker = AsyncMock()
                worker.worker_id = f"worker_{i}"
                worker.is_active = True
                
                if i == 1:  # Worker 1 fails
                    worker.process_task.side_effect = Exception("Worker failed")
                    worker.is_active = False
                elif i == 2:  # Worker 2 fails intermittently
                    worker.process_task.side_effect = [
                        Exception("Temporary failure"),
                        TaskResult(
                            task_id="recovered_task",
                            status=TaskStatus.COMPLETED,
                            worker_id=f"worker_{i}",
                            result={"recovered": True},
                            processing_time=0.2
                        )
                    ]
                else:  # Workers 0 and 3 work normally
                    worker.process_task.return_value = TaskResult(
                        task_id="normal_task",
                        status=TaskStatus.COMPLETED,
                        worker_id=f"worker_{i}",
                        result={"normal": True},
                        processing_time=0.1
                    )
                
                mock_workers.append(worker)
            
            mock_worker_class.side_effect = mock_workers
            
            processor = DistributedProcessor(
                distributed_config=distributed_config,
                milvus_config=milvus_config
            )
            
            await processor.start()
            
            # Test fault tolerance
            tasks = [{"task_id": f"task_{i}", "data": f"data_{i}"} for i in range(10)]
            
            results = await processor.process_tasks_with_fault_tolerance(tasks)
            
            # Verify fault tolerance
            successful_results = [r for r in results if r.status == TaskStatus.COMPLETED]
            failed_results = [r for r in results if r.status == TaskStatus.FAILED]
            
            # Should have some successful results despite worker failures
            assert len(successful_results) > 0
            
            # Test worker recovery
            recovery_stats = await processor.get_recovery_statistics()
            assert recovery_stats["failed_workers"] >= 1
            assert recovery_stats["recovered_workers"] >= 0
            assert recovery_stats["retry_attempts"] > 0

    @pytest.mark.asyncio
    async def test_auto_scaling_functionality(self, distributed_config, milvus_config):
        """Test auto-scaling functionality."""
        with patch('ai_prishtina_milvus_client.distributed.WorkerNode') as mock_worker_class:
            
            # Mock dynamic worker creation
            created_workers = []
            
            def create_worker(*args, **kwargs):
                worker = AsyncMock()
                worker.worker_id = f"worker_{len(created_workers)}"
                worker.is_active = True
                worker.process_task.return_value = TaskResult(
                    task_id="auto_scaled_task",
                    status=TaskStatus.COMPLETED,
                    worker_id=worker.worker_id,
                    result={"auto_scaled": True},
                    processing_time=0.1
                )
                created_workers.append(worker)
                return worker
            
            mock_worker_class.side_effect = create_worker
            
            processor = DistributedProcessor(
                distributed_config=distributed_config,
                milvus_config=milvus_config
            )
            
            await processor.start()
            
            # Simulate high load to trigger auto-scaling
            high_load_tasks = [
                {"task_id": f"load_task_{i}", "data": f"heavy_data_{i}"}
                for i in range(50)
            ]
            
            # Process high load
            start_time = time.time()
            results = await processor.process_tasks_with_auto_scaling(high_load_tasks)
            processing_time = time.time() - start_time
            
            # Verify auto-scaling occurred
            scaling_stats = await processor.get_auto_scaling_statistics()
            assert scaling_stats["scale_up_events"] > 0
            assert scaling_stats["current_workers"] > distributed_config.worker_count
            assert scaling_stats["max_workers_reached"] <= distributed_config.max_workers
            
            # Simulate low load to trigger scale-down
            await asyncio.sleep(2.0)  # Wait for scale-down trigger
            
            low_load_tasks = [
                {"task_id": f"light_task_{i}", "data": f"light_data_{i}"}
                for i in range(5)
            ]
            
            await processor.process_tasks_with_auto_scaling(low_load_tasks)
            
            # Verify scale-down
            final_scaling_stats = await processor.get_auto_scaling_statistics()
            assert final_scaling_stats["scale_down_events"] > 0

    @pytest.mark.asyncio
    async def test_distributed_batch_operations(self, distributed_config, milvus_config):
        """Test distributed batch operations."""
        with patch('ai_prishtina_milvus_client.distributed.WorkerNode') as mock_worker_class:
            
            # Mock workers for batch processing
            mock_workers = []
            for i in range(4):
                worker = AsyncMock()
                worker.worker_id = f"worker_{i}"
                worker.is_active = True
                worker.process_batch.return_value = [
                    TaskResult(
                        task_id=f"batch_task_{j}",
                        status=TaskStatus.COMPLETED,
                        worker_id=f"worker_{i}",
                        result={"batch_item": j, "worker": i},
                        processing_time=0.05
                    )
                    for j in range(25)  # Each worker processes 25 items
                ]
                mock_workers.append(worker)
            
            mock_worker_class.side_effect = mock_workers
            
            processor = DistributedProcessor(
                distributed_config=distributed_config,
                milvus_config=milvus_config
            )
            
            await processor.start()
            
            # Test distributed batch insert
            vectors = [np.random.rand(128).tolist() for _ in range(1000)]
            metadata = [{"id": i, "text": f"doc_{i}"} for i in range(1000)]
            
            start_time = time.time()
            results = await processor.distributed_batch_insert(
                vectors=vectors,
                metadata=metadata,
                batch_size=250  # 4 batches for 4 workers
            )
            processing_time = time.time() - start_time
            
            # Verify batch processing
            assert len(results) == 4  # One result per worker/batch
            total_processed = sum(len(batch_result) for batch_result in results)
            assert total_processed == 1000
            
            # Verify parallel processing improved performance
            batch_stats = await processor.get_batch_processing_statistics()
            assert batch_stats["total_batches"] == 4
            assert batch_stats["parallel_efficiency"] > 0.5  # Should be reasonably efficient
            
            # Test distributed batch search
            query_vectors = [np.random.rand(128).tolist() for _ in range(200)]
            
            search_results = await processor.distributed_batch_search(
                query_vectors=query_vectors,
                top_k=10,
                batch_size=50  # 4 batches for 4 workers
            )
            
            assert len(search_results) == 200  # One result per query

    @pytest.mark.asyncio
    async def test_task_queue_management(self, distributed_config, milvus_config):
        """Test task queue management and prioritization."""
        with patch('ai_prishtina_milvus_client.distributed.WorkerNode') as mock_worker_class:
            
            # Mock workers with different processing speeds
            mock_workers = []
            for i in range(2):
                worker = AsyncMock()
                worker.worker_id = f"worker_{i}"
                worker.is_active = True
                
                async def process_task_with_delay(task):
                    await asyncio.sleep(0.1)  # Simulate processing time
                    return TaskResult(
                        task_id=task["task_id"],
                        status=TaskStatus.COMPLETED,
                        worker_id=worker.worker_id,
                        result={"processed": True, "priority": task.get("priority", 0)},
                        processing_time=0.1
                    )
                
                worker.process_task.side_effect = process_task_with_delay
                mock_workers.append(worker)
            
            mock_worker_class.side_effect = mock_workers
            
            processor = DistributedProcessor(
                distributed_config=distributed_config,
                milvus_config=milvus_config
            )
            
            await processor.start()
            
            # Test task prioritization
            high_priority_tasks = [
                {"task_id": f"high_priority_{i}", "priority": 10, "data": f"urgent_{i}"}
                for i in range(5)
            ]
            
            low_priority_tasks = [
                {"task_id": f"low_priority_{i}", "priority": 1, "data": f"normal_{i}"}
                for i in range(10)
            ]
            
            # Submit low priority tasks first
            await processor.submit_tasks(low_priority_tasks)
            
            # Then submit high priority tasks
            await processor.submit_tasks(high_priority_tasks)
            
            # Process all tasks
            results = await processor.process_all_queued_tasks()
            
            # Verify task queue management
            queue_stats = await processor.get_task_queue_statistics()
            assert queue_stats["total_tasks_processed"] == 15
            assert queue_stats["high_priority_tasks"] == 5
            assert queue_stats["low_priority_tasks"] == 10
            
            # Verify high priority tasks were processed first
            # (This would require more sophisticated mocking to verify order)
            high_priority_results = [r for r in results if r.result.get("priority") == 10]
            low_priority_results = [r for r in results if r.result.get("priority") == 1]
            
            assert len(high_priority_results) == 5
            assert len(low_priority_results) == 10

    @pytest.mark.asyncio
    async def test_distributed_system_monitoring(self, distributed_config, milvus_config):
        """Test distributed system monitoring and metrics."""
        with patch('ai_prishtina_milvus_client.distributed.WorkerNode') as mock_worker_class:
            
            # Mock workers with monitoring capabilities
            mock_workers = []
            for i in range(3):
                worker = AsyncMock()
                worker.worker_id = f"worker_{i}"
                worker.is_active = True
                worker.get_metrics.return_value = {
                    "tasks_processed": 10 + i * 5,
                    "average_processing_time": 0.1 + i * 0.05,
                    "memory_usage": 0.3 + i * 0.1,
                    "cpu_usage": 0.2 + i * 0.15,
                    "error_count": i
                }
                worker.process_task.return_value = TaskResult(
                    task_id="monitored_task",
                    status=TaskStatus.COMPLETED,
                    worker_id=f"worker_{i}",
                    result={"monitored": True},
                    processing_time=0.1 + i * 0.05
                )
                mock_workers.append(worker)
            
            mock_worker_class.side_effect = mock_workers
            
            processor = DistributedProcessor(
                distributed_config=distributed_config,
                milvus_config=milvus_config
            )
            
            await processor.start()
            
            # Process some tasks to generate metrics
            tasks = [{"task_id": f"metric_task_{i}", "data": f"data_{i}"} for i in range(30)]
            await processor.process_tasks_batch(tasks)
            
            # Get comprehensive system metrics
            system_metrics = await processor.get_comprehensive_system_metrics()
            
            # Verify system-level metrics
            assert "cluster_metrics" in system_metrics
            assert "worker_metrics" in system_metrics
            assert "performance_metrics" in system_metrics
            assert "health_metrics" in system_metrics
            
            cluster_metrics = system_metrics["cluster_metrics"]
            assert cluster_metrics["total_workers"] == 3
            assert cluster_metrics["active_workers"] == 3
            assert cluster_metrics["total_tasks_processed"] >= 30
            
            # Verify worker-level metrics
            worker_metrics = system_metrics["worker_metrics"]
            assert len(worker_metrics) == 3
            
            for worker_id, metrics in worker_metrics.items():
                assert "tasks_processed" in metrics
                assert "average_processing_time" in metrics
                assert "memory_usage" in metrics
                assert "cpu_usage" in metrics
                assert "error_count" in metrics
            
            # Verify performance metrics
            performance_metrics = system_metrics["performance_metrics"]
            assert "overall_throughput" in performance_metrics
            assert "average_response_time" in performance_metrics
            assert "system_efficiency" in performance_metrics
            
            # Test real-time monitoring
            monitoring_data = await processor.get_real_time_monitoring_data()
            assert "current_load" in monitoring_data
            assert "active_tasks" in monitoring_data
            assert "queue_size" in monitoring_data
            assert "worker_status" in monitoring_data
