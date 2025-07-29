"""
Comprehensive performance and monitoring tests.

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
import threading
from concurrent.futures import ThreadPoolExecutor

from ai_prishtina_milvus_client.performance import (
    PerformanceOptimizer,
    PerformanceConfig,
    CacheManager,
    ConnectionPool,
    BatchProcessor,
    PerformanceMetrics
)
from ai_prishtina_milvus_client.monitoring import (
    MetricsCollector,
    MonitoringConfig,
    AlertManager,
    HealthChecker,
    PerformanceMonitor
)
from ai_prishtina_milvus_client.config import MilvusConfig
from ai_prishtina_milvus_client.exceptions import PerformanceError, MonitoringError


class TestPerformanceOptimizerComprehensive:
    """Comprehensive performance optimizer tests."""

    @pytest.fixture
    def performance_config(self):
        """Create performance configuration."""
        return PerformanceConfig(
            cache_size=1000,
            connection_pool_size=10,
            batch_size=100,
            timeout=30.0,
            max_retries=3,
            enable_compression=True,
            enable_connection_pooling=True,
            enable_query_caching=True
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
    async def test_performance_optimization_workflow(self, performance_config, milvus_config):
        """Test complete performance optimization workflow."""
        with patch('ai_prishtina_milvus_client.performance.AsyncMilvusClient') as mock_milvus:
            
            # Mock Milvus client
            mock_milvus_instance = AsyncMock()
            mock_milvus_instance.search.return_value = [
                [{"id": i, "distance": 0.1 * i} for i in range(10)]
            ]
            mock_milvus.return_value = mock_milvus_instance
            
            optimizer = PerformanceOptimizer(
                performance_config=performance_config,
                milvus_config=milvus_config
            )
            
            await optimizer.initialize()
            
            # Test optimized search with caching
            query_vector = np.random.rand(128).tolist()
            
            # First search (cache miss)
            start_time = time.time()
            results1 = await optimizer.optimized_search(
                query_vector=query_vector,
                top_k=10,
                search_params={"nprobe": 16}
            )
            first_search_time = time.time() - start_time
            
            # Second search (cache hit)
            start_time = time.time()
            results2 = await optimizer.optimized_search(
                query_vector=query_vector,
                top_k=10,
                search_params={"nprobe": 16}
            )
            second_search_time = time.time() - start_time
            
            # Verify caching improved performance
            assert second_search_time < first_search_time
            assert results1 == results2
            
            # Verify Milvus was called only once (second was cached)
            mock_milvus_instance.search.assert_called_once()

    @pytest.mark.asyncio
    async def test_batch_processing_optimization(self, performance_config, milvus_config):
        """Test batch processing optimization."""
        with patch('ai_prishtina_milvus_client.performance.AsyncMilvusClient') as mock_milvus:
            
            mock_milvus_instance = AsyncMock()
            mock_milvus_instance.insert.return_value = list(range(1000))
            mock_milvus.return_value = mock_milvus_instance
            
            optimizer = PerformanceOptimizer(
                performance_config=performance_config,
                milvus_config=milvus_config
            )
            
            await optimizer.initialize()
            
            # Test batch insert optimization
            vectors = [np.random.rand(128).tolist() for _ in range(1000)]
            metadata = [{"id": i, "text": f"doc_{i}"} for i in range(1000)]
            
            start_time = time.time()
            results = await optimizer.optimized_batch_insert(
                vectors=vectors,
                metadata=metadata,
                batch_size=100
            )
            processing_time = time.time() - start_time
            
            # Verify all vectors were processed
            assert len(results) == 1000
            
            # Verify batching was used (10 batches of 100)
            assert mock_milvus_instance.insert.call_count == 10
            
            # Verify performance metrics
            metrics = optimizer.get_performance_metrics()
            assert metrics["total_operations"] >= 10
            assert metrics["average_batch_size"] == 100
            assert metrics["total_processing_time"] > 0

    @pytest.mark.asyncio
    async def test_connection_pool_optimization(self, performance_config, milvus_config):
        """Test connection pool optimization."""
        with patch('ai_prishtina_milvus_client.performance.AsyncMilvusClient') as mock_milvus:
            
            # Mock multiple client instances for pool
            mock_clients = [AsyncMock() for _ in range(performance_config.connection_pool_size)]
            for i, client in enumerate(mock_clients):
                client.search.return_value = [[{"id": i, "distance": 0.1}]]
            
            mock_milvus.side_effect = mock_clients
            
            optimizer = PerformanceOptimizer(
                performance_config=performance_config,
                milvus_config=milvus_config
            )
            
            await optimizer.initialize()
            
            # Test concurrent operations using connection pool
            async def concurrent_search(query_id):
                query_vector = np.random.rand(128).tolist()
                return await optimizer.optimized_search(
                    query_vector=query_vector,
                    top_k=5,
                    search_params={"nprobe": 8}
                )
            
            # Run multiple concurrent searches
            tasks = [concurrent_search(i) for i in range(20)]
            results = await asyncio.gather(*tasks)
            
            # Verify all searches completed
            assert len(results) == 20
            
            # Verify connection pool was utilized
            pool_metrics = optimizer.get_connection_pool_metrics()
            assert pool_metrics["pool_size"] == performance_config.connection_pool_size
            assert pool_metrics["active_connections"] <= performance_config.connection_pool_size
            assert pool_metrics["total_requests"] >= 20

    @pytest.mark.asyncio
    async def test_query_optimization_strategies(self, performance_config, milvus_config):
        """Test various query optimization strategies."""
        with patch('ai_prishtina_milvus_client.performance.AsyncMilvusClient') as mock_milvus:
            
            mock_milvus_instance = AsyncMock()
            mock_milvus_instance.search.return_value = [
                [{"id": i, "distance": 0.1 * i} for i in range(100)]
            ]
            mock_milvus.return_value = mock_milvus_instance
            
            optimizer = PerformanceOptimizer(
                performance_config=performance_config,
                milvus_config=milvus_config
            )
            
            await optimizer.initialize()
            
            query_vector = np.random.rand(128).tolist()
            
            # Test different optimization strategies
            strategies = [
                {"strategy": "high_accuracy", "nprobe": 64},
                {"strategy": "balanced", "nprobe": 16},
                {"strategy": "high_speed", "nprobe": 4}
            ]
            
            results = {}
            for strategy in strategies:
                start_time = time.time()
                result = await optimizer.optimized_search(
                    query_vector=query_vector,
                    top_k=10,
                    search_params={"nprobe": strategy["nprobe"]},
                    optimization_strategy=strategy["strategy"]
                )
                end_time = time.time()
                
                results[strategy["strategy"]] = {
                    "result": result,
                    "time": end_time - start_time,
                    "nprobe": strategy["nprobe"]
                }
            
            # Verify different strategies were applied
            assert len(results) == 3
            
            # High speed should generally be faster (though with mocks, timing may vary)
            # Verify nprobe parameters were used correctly
            for strategy_name, data in results.items():
                assert len(data["result"]) == 1  # One query result
                assert len(data["result"][0]) <= 10  # Top-k results


class TestMonitoringComprehensive:
    """Comprehensive monitoring tests."""

    @pytest.fixture
    def monitoring_config(self):
        """Create monitoring configuration."""
        return MonitoringConfig(
            metrics_collection_interval=1.0,
            alert_thresholds={
                "response_time": 5.0,
                "error_rate": 0.05,
                "memory_usage": 0.8,
                "cpu_usage": 0.9
            },
            enable_health_checks=True,
            health_check_interval=30.0,
            enable_performance_monitoring=True,
            enable_alerting=True
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
    async def test_comprehensive_metrics_collection(self, monitoring_config, milvus_config):
        """Test comprehensive metrics collection."""
        with patch('ai_prishtina_milvus_client.monitoring.AsyncMilvusClient') as mock_milvus, \
             patch('psutil.cpu_percent') as mock_cpu, \
             patch('psutil.virtual_memory') as mock_memory:
            
            # Mock system metrics
            mock_cpu.return_value = 45.5
            mock_memory.return_value = Mock(percent=65.2, available=1024*1024*1024)
            
            # Mock Milvus client
            mock_milvus_instance = AsyncMock()
            mock_milvus_instance.get_collection_stats.return_value = {
                "row_count": 10000,
                "data_size": 1024*1024*50  # 50MB
            }
            mock_milvus.return_value = mock_milvus_instance
            
            collector = MetricsCollector(
                monitoring_config=monitoring_config,
                milvus_config=milvus_config
            )
            
            await collector.start_collection()
            
            # Simulate some operations
            await collector.record_operation("search", duration=0.5, success=True)
            await collector.record_operation("insert", duration=1.2, success=True)
            await collector.record_operation("search", duration=0.3, success=False)
            
            # Wait for metrics collection
            await asyncio.sleep(1.5)
            
            # Get collected metrics
            metrics = await collector.get_metrics()
            
            # Verify system metrics
            assert "cpu_usage" in metrics
            assert "memory_usage" in metrics
            assert metrics["cpu_usage"] == 45.5
            assert metrics["memory_usage"] == 65.2
            
            # Verify operation metrics
            assert "operations" in metrics
            assert metrics["operations"]["search"]["total_count"] == 2
            assert metrics["operations"]["search"]["success_count"] == 1
            assert metrics["operations"]["search"]["error_count"] == 1
            assert metrics["operations"]["search"]["average_duration"] == 0.4  # (0.5 + 0.3) / 2
            
            # Verify collection metrics
            assert "collection_stats" in metrics
            assert metrics["collection_stats"]["row_count"] == 10000
            
            await collector.stop_collection()

    @pytest.mark.asyncio
    async def test_alert_management_system(self, monitoring_config, milvus_config):
        """Test comprehensive alert management."""
        with patch('ai_prishtina_milvus_client.monitoring.AsyncMilvusClient') as mock_milvus:
            
            mock_milvus_instance = AsyncMock()
            mock_milvus.return_value = mock_milvus_instance
            
            alert_manager = AlertManager(
                monitoring_config=monitoring_config,
                milvus_config=milvus_config
            )
            
            await alert_manager.initialize()
            
            # Test different alert scenarios
            alert_scenarios = [
                {
                    "metric": "response_time",
                    "value": 6.0,  # Above threshold of 5.0
                    "expected_alert": True
                },
                {
                    "metric": "error_rate",
                    "value": 0.08,  # Above threshold of 0.05
                    "expected_alert": True
                },
                {
                    "metric": "memory_usage",
                    "value": 0.85,  # Above threshold of 0.8
                    "expected_alert": True
                },
                {
                    "metric": "cpu_usage",
                    "value": 0.7,  # Below threshold of 0.9
                    "expected_alert": False
                }
            ]
            
            triggered_alerts = []
            
            # Mock alert handler
            async def mock_alert_handler(alert):
                triggered_alerts.append(alert)
            
            alert_manager.register_alert_handler(mock_alert_handler)
            
            # Process alert scenarios
            for scenario in alert_scenarios:
                await alert_manager.check_metric(
                    metric_name=scenario["metric"],
                    value=scenario["value"]
                )
            
            # Verify alerts were triggered correctly
            expected_alerts = sum(1 for s in alert_scenarios if s["expected_alert"])
            assert len(triggered_alerts) == expected_alerts
            
            # Verify alert content
            for alert in triggered_alerts:
                assert "metric_name" in alert
                assert "value" in alert
                assert "threshold" in alert
                assert "timestamp" in alert
                assert alert["value"] > alert["threshold"]

    @pytest.mark.asyncio
    async def test_health_check_system(self, monitoring_config, milvus_config):
        """Test comprehensive health check system."""
        with patch('ai_prishtina_milvus_client.monitoring.AsyncMilvusClient') as mock_milvus:
            
            mock_milvus_instance = AsyncMock()
            mock_milvus_instance.ping.return_value = True
            mock_milvus_instance.list_collections.return_value = ["test_collection"]
            mock_milvus_instance.get_collection_stats.return_value = {"row_count": 1000}
            mock_milvus.return_value = mock_milvus_instance
            
            health_checker = HealthChecker(
                monitoring_config=monitoring_config,
                milvus_config=milvus_config
            )
            
            await health_checker.initialize()
            
            # Test comprehensive health check
            health_status = await health_checker.comprehensive_health_check()
            
            # Verify health check components
            assert "milvus_connection" in health_status
            assert "collection_status" in health_status
            assert "system_resources" in health_status
            assert "overall_status" in health_status
            
            # Verify Milvus connection health
            assert health_status["milvus_connection"]["status"] == "healthy"
            assert health_status["milvus_connection"]["ping_success"] is True
            
            # Verify collection health
            assert health_status["collection_status"]["exists"] is True
            assert health_status["collection_status"]["row_count"] == 1000
            
            # Verify overall status
            assert health_status["overall_status"] == "healthy"

    @pytest.mark.asyncio
    async def test_performance_monitoring_integration(self, monitoring_config, milvus_config):
        """Test performance monitoring integration."""
        with patch('ai_prishtina_milvus_client.monitoring.AsyncMilvusClient') as mock_milvus:
            
            mock_milvus_instance = AsyncMock()
            mock_milvus_instance.search.return_value = [
                [{"id": i, "distance": 0.1 * i} for i in range(10)]
            ]
            mock_milvus.return_value = mock_milvus_instance
            
            monitor = PerformanceMonitor(
                monitoring_config=monitoring_config,
                milvus_config=milvus_config
            )
            
            await monitor.start_monitoring()
            
            # Simulate various operations with different performance characteristics
            operations = [
                {"type": "search", "duration": 0.1, "success": True},
                {"type": "search", "duration": 0.2, "success": True},
                {"type": "search", "duration": 2.5, "success": True},  # Slow operation
                {"type": "insert", "duration": 1.0, "success": True},
                {"type": "search", "duration": 0.15, "success": False},  # Failed operation
            ]
            
            for op in operations:
                await monitor.record_operation(
                    operation_type=op["type"],
                    duration=op["duration"],
                    success=op["success"]
                )
            
            # Wait for monitoring to process
            await asyncio.sleep(0.1)
            
            # Get performance report
            report = await monitor.generate_performance_report()
            
            # Verify performance metrics
            assert "operation_metrics" in report
            assert "search" in report["operation_metrics"]
            assert "insert" in report["operation_metrics"]
            
            search_metrics = report["operation_metrics"]["search"]
            assert search_metrics["total_operations"] == 4
            assert search_metrics["successful_operations"] == 3
            assert search_metrics["failed_operations"] == 1
            assert search_metrics["average_duration"] > 0
            assert search_metrics["max_duration"] == 2.5
            assert search_metrics["min_duration"] == 0.1
            
            # Verify performance trends
            assert "performance_trends" in report
            assert "response_time_trend" in report["performance_trends"]
            assert "error_rate_trend" in report["performance_trends"]
            
            await monitor.stop_monitoring()

    @pytest.mark.asyncio
    async def test_real_time_monitoring_dashboard(self, monitoring_config, milvus_config):
        """Test real-time monitoring dashboard functionality."""
        with patch('ai_prishtina_milvus_client.monitoring.AsyncMilvusClient') as mock_milvus:
            
            mock_milvus_instance = AsyncMock()
            mock_milvus.return_value = mock_milvus_instance
            
            monitor = PerformanceMonitor(
                monitoring_config=monitoring_config,
                milvus_config=milvus_config
            )
            
            await monitor.start_monitoring()
            
            # Simulate real-time data collection
            for i in range(10):
                await monitor.record_operation(
                    operation_type="search",
                    duration=0.1 + (i * 0.05),  # Gradually increasing response time
                    success=i < 8  # Last 2 operations fail
                )
                await asyncio.sleep(0.1)
            
            # Get real-time dashboard data
            dashboard_data = await monitor.get_real_time_dashboard_data()
            
            # Verify dashboard components
            assert "current_metrics" in dashboard_data
            assert "recent_operations" in dashboard_data
            assert "alerts" in dashboard_data
            assert "system_status" in dashboard_data
            
            # Verify current metrics
            current_metrics = dashboard_data["current_metrics"]
            assert "operations_per_second" in current_metrics
            assert "average_response_time" in current_metrics
            assert "error_rate" in current_metrics
            assert "active_connections" in current_metrics
            
            # Verify recent operations tracking
            recent_ops = dashboard_data["recent_operations"]
            assert len(recent_ops) <= 10  # Should track recent operations
            
            # Verify error rate calculation
            assert current_metrics["error_rate"] == 0.2  # 2 failures out of 10
            
            await monitor.stop_monitoring()
