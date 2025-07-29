"""
End-to-end integration tests that combine multiple services.

Copyright (c) 2025 Alban Maxhuni <alban.q.maxhuni@gmail.com>

This software is dual-licensed under AGPL-3.0 (open-source) and Commercial licenses.
For commercial licensing, contact: alban.q.maxhuni@gmail.com
"""

import pytest
import asyncio
import json
import time
import numpy as np
from typing import List, Dict, Any

from ai_prishtina_milvus_client.client import AsyncMilvusClient
from ai_prishtina_milvus_client.streaming import KafkaStreamProcessor, StreamMessage
from ai_prishtina_milvus_client.security import SecurityManager
from ai_prishtina_milvus_client.exceptions import *


@pytest.mark.integration
@pytest.mark.docker
@pytest.mark.slow
class TestEndToEndIntegration:
    """End-to-end integration tests combining multiple services."""

    @pytest.mark.asyncio
    async def test_complete_vector_pipeline(
        self, 
        docker_services, 
        milvus_config, 
        kafka_config, 
        security_config,
        sample_vectors, 
        sample_metadata
    ):
        """Test complete vector processing pipeline."""
        # Initialize all components
        milvus_client = AsyncMilvusClient(milvus_config)
        security_manager = SecurityManager(config=security_config)
        
        try:
            # 1. Setup security
            await security_manager.create_user(
                username="pipeline_user",
                password="secure_password",
                roles=["read", "write", "admin"]
            )
            
            # Authenticate user
            auth_token = await security_manager.authenticate("pipeline_user", "secure_password")
            assert auth_token is not None
            
            # 2. Setup Milvus
            await milvus_client.connect()
            
            collection_name = "e2e_test_collection"
            await milvus_client.create_collection(
                collection_name=collection_name,
                dimension=128,
                index_type="IVF_FLAT",
                metric_type="L2"
            )
            
            # 3. Process data through streaming pipeline
            from unittest.mock import AsyncMock, patch
            
            with patch('ai_prishtina_milvus_client.streaming.AsyncMilvusClient') as mock_stream_client:
                mock_stream_client_instance = AsyncMock()
                mock_stream_client_instance.insert.return_value = list(range(len(sample_vectors)))
                mock_stream_client.return_value = mock_stream_client_instance
                
                stream_processor = KafkaStreamProcessor(
                    milvus_config=milvus_config,
                    stream_config=kafka_config
                )
                
                # Create stream message
                stream_message = StreamMessage(
                    vectors=sample_vectors,
                    metadata=sample_metadata,
                    operation="insert",
                    collection=collection_name
                )
                
                # Process through streaming
                await stream_processor.produce_message("vector_pipeline", stream_message)
            
            # 4. Insert data directly to Milvus for verification
            encrypted_metadata = []
            for metadata in sample_metadata:
                encrypted_meta = metadata.copy()
                if "category" in encrypted_meta:
                    # Encrypt sensitive data
                    encrypted_category = await security_manager.encrypt_data(encrypted_meta["category"])
                    encrypted_meta["encrypted_category"] = encrypted_category.decode() if isinstance(encrypted_category, bytes) else encrypted_category
                encrypted_metadata.append(encrypted_meta)
            
            ids = await milvus_client.insert(
                collection_name=collection_name,
                vectors=sample_vectors,
                metadata=encrypted_metadata
            )
            
            assert len(ids) == len(sample_vectors)
            
            # Wait for indexing
            await asyncio.sleep(3)
            
            # 5. Search and verify results
            query_vector = sample_vectors[0]
            search_results = await milvus_client.search(
                collection_name=collection_name,
                query_vectors=[query_vector],
                top_k=5,
                search_params={"nprobe": 10}
            )
            
            assert len(search_results) == 1
            assert len(search_results[0]) > 0
            assert search_results[0][0]["distance"] < 0.1  # Should find exact match
            
            # 6. Decrypt and verify metadata
            result_metadata = search_results[0][0]["metadata"]
            if "encrypted_category" in result_metadata:
                decrypted_category = await security_manager.decrypt_data(
                    result_metadata["encrypted_category"].encode() 
                    if isinstance(result_metadata["encrypted_category"], str) 
                    else result_metadata["encrypted_category"]
                )
                assert decrypted_category == sample_metadata[0]["category"]
            
            # 7. Cleanup
            await milvus_client.drop_collection(collection_name)
            
        finally:
            await milvus_client.disconnect()

    @pytest.mark.asyncio
    async def test_high_availability_scenario(
        self, 
        docker_services, 
        milvus_config, 
        redis_client,
        sample_vectors
    ):
        """Test high availability and failover scenarios."""
        milvus_client = AsyncMilvusClient(milvus_config)
        
        try:
            await milvus_client.connect()
            
            collection_name = "ha_test_collection"
            await milvus_client.create_collection(
                collection_name=collection_name,
                dimension=128,
                index_type="IVF_FLAT",
                metric_type="L2"
            )
            
            # 1. Normal operation - insert data
            batch_1_ids = await milvus_client.insert(
                collection_name=collection_name,
                vectors=sample_vectors[:5],
                metadata=[{"batch": 1, "id": i} for i in range(5)]
            )
            
            # 2. Cache results in Redis for failover
            cache_key = f"milvus_backup:{collection_name}:batch_1"
            cache_data = {
                "vectors": sample_vectors[:5],
                "metadata": [{"batch": 1, "id": i} for i in range(5)],
                "ids": batch_1_ids,
                "timestamp": time.time()
            }
            
            redis_client.setex(cache_key, 3600, json.dumps(cache_data))
            
            # 3. Simulate partial failure - continue with cached data
            cached_data = redis_client.get(cache_key)
            assert cached_data is not None
            
            restored_data = json.loads(cached_data)
            assert len(restored_data["vectors"]) == 5
            assert len(restored_data["ids"]) == 5
            
            # 4. Recovery - insert remaining data
            batch_2_ids = await milvus_client.insert(
                collection_name=collection_name,
                vectors=sample_vectors[5:],
                metadata=[{"batch": 2, "id": i} for i in range(5, len(sample_vectors))]
            )
            
            # Wait for indexing
            await asyncio.sleep(2)
            
            # 5. Verify complete dataset
            total_count = await milvus_client.count(collection_name)
            assert total_count == len(sample_vectors)
            
            # 6. Test search across all data
            query_vector = sample_vectors[0]
            search_results = await milvus_client.search(
                collection_name=collection_name,
                query_vectors=[query_vector],
                top_k=10
            )
            
            assert len(search_results[0]) > 0
            
            # Cleanup
            await milvus_client.drop_collection(collection_name)
            
        finally:
            await milvus_client.disconnect()

    @pytest.mark.asyncio
    async def test_performance_under_load(
        self, 
        docker_services, 
        milvus_config,
        prometheus_config
    ):
        """Test system performance under load."""
        milvus_client = AsyncMilvusClient(milvus_config)
        
        try:
            await milvus_client.connect()
            
            collection_name = "performance_test_collection"
            await milvus_client.create_collection(
                collection_name=collection_name,
                dimension=128,
                index_type="IVF_FLAT",
                metric_type="L2"
            )
            
            # Performance test parameters
            batch_size = 1000
            num_batches = 5
            concurrent_searches = 10
            
            # 1. Load test - insert large amounts of data
            insert_times = []
            total_vectors = 0
            
            for batch_idx in range(num_batches):
                vectors = np.random.rand(batch_size, 128).tolist()
                metadata = [
                    {"batch": batch_idx, "item": i, "timestamp": time.time()}
                    for i in range(batch_size)
                ]
                
                start_time = time.time()
                ids = await milvus_client.insert(
                    collection_name=collection_name,
                    vectors=vectors,
                    metadata=metadata
                )
                insert_time = time.time() - start_time
                insert_times.append(insert_time)
                
                assert len(ids) == batch_size
                total_vectors += batch_size
                
                # Brief pause between batches
                await asyncio.sleep(0.5)
            
            # Wait for indexing
            await asyncio.sleep(10)
            
            # 2. Concurrent search test
            async def perform_search(search_id: int):
                query_vector = np.random.rand(128).tolist()
                start_time = time.time()
                
                results = await milvus_client.search(
                    collection_name=collection_name,
                    query_vectors=[query_vector],
                    top_k=10,
                    search_params={"nprobe": 10}
                )
                
                search_time = time.time() - start_time
                return {
                    "search_id": search_id,
                    "search_time": search_time,
                    "results_count": len(results[0]) if results else 0
                }
            
            # Run concurrent searches
            search_tasks = [perform_search(i) for i in range(concurrent_searches)]
            search_results = await asyncio.gather(*search_tasks)
            
            # 3. Analyze performance metrics
            avg_insert_time = sum(insert_times) / len(insert_times)
            total_insert_time = sum(insert_times)
            insert_throughput = total_vectors / total_insert_time
            
            search_times = [r["search_time"] for r in search_results]
            avg_search_time = sum(search_times) / len(search_times)
            max_search_time = max(search_times)
            min_search_time = min(search_times)
            
            # Verify performance is within acceptable bounds
            assert avg_insert_time < 5.0  # Average insert should be under 5 seconds
            assert insert_throughput > 100  # Should insert at least 100 vectors/second
            assert avg_search_time < 1.0  # Average search should be under 1 second
            assert all(r["results_count"] > 0 for r in search_results)  # All searches should return results
            
            # Log performance metrics
            print(f"Performance Test Results:")
            print(f"  Total vectors inserted: {total_vectors}")
            print(f"  Average insert time: {avg_insert_time:.3f}s")
            print(f"  Insert throughput: {insert_throughput:.1f} vectors/s")
            print(f"  Average search time: {avg_search_time:.3f}s")
            print(f"  Search time range: {min_search_time:.3f}s - {max_search_time:.3f}s")
            
            # 4. Verify data integrity
            final_count = await milvus_client.count(collection_name)
            assert final_count == total_vectors
            
            # Cleanup
            await milvus_client.drop_collection(collection_name)
            
        finally:
            await milvus_client.disconnect()

    @pytest.mark.asyncio
    async def test_data_consistency_across_services(
        self, 
        docker_services, 
        milvus_config, 
        redis_client,
        minio_config,
        sample_vectors, 
        sample_metadata
    ):
        """Test data consistency across multiple services."""
        milvus_client = AsyncMilvusClient(milvus_config)
        
        try:
            await milvus_client.connect()
            
            collection_name = "consistency_test_collection"
            await milvus_client.create_collection(
                collection_name=collection_name,
                dimension=128,
                index_type="IVF_FLAT",
                metric_type="L2"
            )
            
            # 1. Insert data into Milvus
            ids = await milvus_client.insert(
                collection_name=collection_name,
                vectors=sample_vectors,
                metadata=sample_metadata
            )
            
            # 2. Store metadata in Redis
            for i, (vector_id, metadata) in enumerate(zip(ids, sample_metadata)):
                redis_key = f"vector_metadata:{collection_name}:{vector_id}"
                redis_data = {
                    "metadata": metadata,
                    "vector_index": i,
                    "collection": collection_name,
                    "created_at": time.time()
                }
                redis_client.setex(redis_key, 3600, json.dumps(redis_data))
            
            # 3. Backup data to MinIO (S3)
            import boto3
            from botocore.exceptions import ClientError
            
            s3_client = boto3.client(
                's3',
                endpoint_url=minio_config["endpoint_url"],
                aws_access_key_id=minio_config["access_key"],
                aws_secret_access_key=minio_config["secret_key"]
            )
            
            # Create bucket if not exists
            try:
                s3_client.create_bucket(Bucket=minio_config["bucket_name"])
            except ClientError:
                pass
            
            backup_data = {
                "collection_name": collection_name,
                "vectors": sample_vectors,
                "metadata": sample_metadata,
                "milvus_ids": ids,
                "backup_timestamp": time.time(),
                "vector_count": len(sample_vectors)
            }
            
            backup_key = f"backups/{collection_name}/backup_{int(time.time())}.json"
            s3_client.put_object(
                Bucket=minio_config["bucket_name"],
                Key=backup_key,
                Body=json.dumps(backup_data).encode('utf-8'),
                ContentType='application/json'
            )
            
            # Wait for indexing
            await asyncio.sleep(3)
            
            # 4. Verify consistency across all services
            
            # Verify Milvus data
            milvus_count = await milvus_client.count(collection_name)
            assert milvus_count == len(sample_vectors)
            
            # Verify Redis data
            redis_keys = redis_client.keys(f"vector_metadata:{collection_name}:*")
            assert len(redis_keys) == len(ids)
            
            for redis_key in redis_keys:
                redis_data = json.loads(redis_client.get(redis_key))
                assert redis_data["collection"] == collection_name
                assert "metadata" in redis_data
                assert "vector_index" in redis_data
            
            # Verify MinIO backup
            backup_response = s3_client.get_object(
                Bucket=minio_config["bucket_name"],
                Key=backup_key
            )
            restored_backup = json.loads(backup_response['Body'].read().decode('utf-8'))
            
            assert restored_backup["collection_name"] == collection_name
            assert len(restored_backup["vectors"]) == len(sample_vectors)
            assert len(restored_backup["metadata"]) == len(sample_metadata)
            assert len(restored_backup["milvus_ids"]) == len(ids)
            
            # 5. Test cross-service data retrieval
            # Search in Milvus and verify metadata in Redis
            query_vector = sample_vectors[0]
            search_results = await milvus_client.search(
                collection_name=collection_name,
                query_vectors=[query_vector],
                top_k=3
            )
            
            for result in search_results[0]:
                milvus_id = result["id"]
                redis_key = f"vector_metadata:{collection_name}:{milvus_id}"
                redis_data = redis_client.get(redis_key)
                
                assert redis_data is not None
                redis_metadata = json.loads(redis_data)
                
                # Verify metadata consistency
                assert redis_metadata["collection"] == collection_name
                
            # Cleanup
            await milvus_client.drop_collection(collection_name)
            
            # Cleanup Redis
            for redis_key in redis_keys:
                redis_client.delete(redis_key)
            
            # Cleanup MinIO
            s3_client.delete_object(
                Bucket=minio_config["bucket_name"],
                Key=backup_key
            )
            
        finally:
            await milvus_client.disconnect()

    @pytest.mark.asyncio
    async def test_disaster_recovery_scenario(
        self, 
        docker_services, 
        milvus_config, 
        redis_client,
        minio_config,
        sample_vectors, 
        sample_metadata
    ):
        """Test disaster recovery procedures."""
        milvus_client = AsyncMilvusClient(milvus_config)
        
        try:
            await milvus_client.connect()
            
            collection_name = "disaster_recovery_test"
            
            # 1. Setup initial data
            await milvus_client.create_collection(
                collection_name=collection_name,
                dimension=128,
                index_type="IVF_FLAT",
                metric_type="L2"
            )
            
            ids = await milvus_client.insert(
                collection_name=collection_name,
                vectors=sample_vectors,
                metadata=sample_metadata
            )
            
            # 2. Create comprehensive backup
            backup_data = {
                "collection_info": {
                    "name": collection_name,
                    "dimension": 128,
                    "index_type": "IVF_FLAT",
                    "metric_type": "L2"
                },
                "vectors": sample_vectors,
                "metadata": sample_metadata,
                "milvus_ids": ids,
                "backup_timestamp": time.time(),
                "backup_version": "1.0"
            }
            
            # Store backup in multiple locations
            # Redis backup
            redis_backup_key = f"disaster_backup:{collection_name}"
            redis_client.setex(redis_backup_key, 86400, json.dumps(backup_data))  # 24 hours
            
            # MinIO backup
            import boto3
            s3_client = boto3.client(
                's3',
                endpoint_url=minio_config["endpoint_url"],
                aws_access_key_id=minio_config["access_key"],
                aws_secret_access_key=minio_config["secret_key"]
            )
            
            try:
                s3_client.create_bucket(Bucket=minio_config["bucket_name"])
            except:
                pass
            
            s3_backup_key = f"disaster_recovery/{collection_name}/full_backup.json"
            s3_client.put_object(
                Bucket=minio_config["bucket_name"],
                Key=s3_backup_key,
                Body=json.dumps(backup_data).encode('utf-8'),
                ContentType='application/json'
            )
            
            # 3. Simulate disaster - drop collection
            await milvus_client.drop_collection(collection_name)
            
            # Verify data is gone
            collections = await milvus_client.list_collections()
            assert collection_name not in collections
            
            # 4. Recovery procedure
            
            # Try Redis recovery first (faster)
            redis_backup = redis_client.get(redis_backup_key)
            if redis_backup:
                recovery_data = json.loads(redis_backup)
                print("Recovering from Redis backup...")
            else:
                # Fallback to S3 recovery
                s3_response = s3_client.get_object(
                    Bucket=minio_config["bucket_name"],
                    Key=s3_backup_key
                )
                recovery_data = json.loads(s3_response['Body'].read().decode('utf-8'))
                print("Recovering from S3 backup...")
            
            # 5. Restore collection
            collection_info = recovery_data["collection_info"]
            await milvus_client.create_collection(
                collection_name=collection_info["name"],
                dimension=collection_info["dimension"],
                index_type=collection_info["index_type"],
                metric_type=collection_info["metric_type"]
            )
            
            # Restore data
            restored_ids = await milvus_client.insert(
                collection_name=collection_name,
                vectors=recovery_data["vectors"],
                metadata=recovery_data["metadata"]
            )
            
            # Wait for indexing
            await asyncio.sleep(3)
            
            # 6. Verify recovery
            restored_count = await milvus_client.count(collection_name)
            assert restored_count == len(sample_vectors)
            
            # Test search functionality
            query_vector = sample_vectors[0]
            search_results = await milvus_client.search(
                collection_name=collection_name,
                query_vectors=[query_vector],
                top_k=5
            )
            
            assert len(search_results[0]) > 0
            assert search_results[0][0]["distance"] < 0.1  # Should find exact match
            
            print(f"Disaster recovery successful! Restored {restored_count} vectors.")
            
            # Cleanup
            await milvus_client.drop_collection(collection_name)
            redis_client.delete(redis_backup_key)
            s3_client.delete_object(Bucket=minio_config["bucket_name"], Key=s3_backup_key)
            
        finally:
            await milvus_client.disconnect()
