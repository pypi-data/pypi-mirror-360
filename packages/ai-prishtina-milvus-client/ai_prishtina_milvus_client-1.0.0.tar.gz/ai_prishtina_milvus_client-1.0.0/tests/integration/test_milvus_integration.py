"""
Integration tests for Milvus operations using Docker containers.
"""

import pytest
import asyncio
import numpy as np
from typing import List, Dict, Any

from ai_prishtina_milvus_client.client import AsyncMilvusClient
from ai_prishtina_milvus_client.config import MilvusConfig
from ai_prishtina_milvus_client.exceptions import (
    ConnectionError, CollectionError, InsertError, SearchError
)


@pytest.mark.integration
@pytest.mark.docker
class TestMilvusIntegration:
    """Integration tests for Milvus operations."""

    @pytest.mark.asyncio
    async def test_milvus_connection(self, docker_services, milvus_config):
        """Test basic Milvus connection."""
        client = AsyncMilvusClient(milvus_config)
        
        try:
            # Test connection
            await client.connect()
            assert client.is_connected()
            
            # Test health check
            health = await client.health_check()
            assert health["status"] == "healthy"
            
        finally:
            await client.disconnect()

    @pytest.mark.asyncio
    async def test_collection_lifecycle(self, docker_services, milvus_config, sample_vectors):
        """Test complete collection lifecycle."""
        client = AsyncMilvusClient(milvus_config)
        
        try:
            await client.connect()
            
            # Create collection
            collection_name = "test_lifecycle_collection"
            await client.create_collection(
                collection_name=collection_name,
                dimension=128,
                index_type="IVF_FLAT",
                metric_type="L2"
            )
            
            # Verify collection exists
            collections = await client.list_collections()
            assert collection_name in collections
            
            # Get collection info
            info = await client.get_collection_info(collection_name)
            assert info["name"] == collection_name
            assert info["dimension"] == 128
            
            # Drop collection
            await client.drop_collection(collection_name)
            
            # Verify collection is dropped
            collections = await client.list_collections()
            assert collection_name not in collections
            
        finally:
            await client.disconnect()

    @pytest.mark.asyncio
    async def test_vector_operations(self, docker_services, milvus_config, sample_vectors, sample_metadata):
        """Test vector insert, search, and delete operations."""
        client = AsyncMilvusClient(milvus_config)
        
        try:
            await client.connect()
            
            collection_name = "test_vector_ops"
            
            # Create collection
            await client.create_collection(
                collection_name=collection_name,
                dimension=128,
                index_type="IVF_FLAT",
                metric_type="L2"
            )
            
            # Insert vectors
            ids = await client.insert(
                collection_name=collection_name,
                vectors=sample_vectors,
                metadata=sample_metadata
            )
            
            assert len(ids) == len(sample_vectors)
            assert all(isinstance(id_, int) for id_ in ids)
            
            # Wait for indexing
            await asyncio.sleep(2)
            
            # Search vectors
            query_vector = sample_vectors[0]
            results = await client.search(
                collection_name=collection_name,
                query_vectors=[query_vector],
                top_k=5,
                search_params={"nprobe": 10}
            )
            
            assert len(results) == 1  # One query vector
            assert len(results[0]) <= 5  # Top K results
            assert results[0][0]["distance"] < 0.1  # Should find exact match
            
            # Test search with metadata filter
            filtered_results = await client.search(
                collection_name=collection_name,
                query_vectors=[query_vector],
                top_k=5,
                filter_expr="category == 'category_0'"
            )
            
            assert len(filtered_results) == 1
            
            # Delete vectors
            delete_ids = ids[:3]
            await client.delete(
                collection_name=collection_name,
                ids=delete_ids
            )
            
            # Verify deletion
            remaining_count = await client.count(collection_name)
            assert remaining_count == len(sample_vectors) - len(delete_ids)
            
            # Cleanup
            await client.drop_collection(collection_name)
            
        finally:
            await client.disconnect()

    @pytest.mark.asyncio
    async def test_batch_operations(self, docker_services, milvus_config):
        """Test batch insert and search operations."""
        client = AsyncMilvusClient(milvus_config)
        
        try:
            await client.connect()
            
            collection_name = "test_batch_ops"
            
            # Create collection
            await client.create_collection(
                collection_name=collection_name,
                dimension=128,
                index_type="IVF_FLAT",
                metric_type="L2"
            )
            
            # Generate large batch of vectors
            batch_size = 1000
            large_vectors = np.random.rand(batch_size, 128).tolist()
            large_metadata = [
                {"id": i, "batch": i // 100, "category": f"cat_{i % 5}"}
                for i in range(batch_size)
            ]
            
            # Batch insert
            ids = await client.batch_insert(
                collection_name=collection_name,
                vectors=large_vectors,
                metadata=large_metadata,
                batch_size=100
            )
            
            assert len(ids) == batch_size
            
            # Wait for indexing
            await asyncio.sleep(5)
            
            # Batch search
            query_vectors = large_vectors[:10]
            results = await client.batch_search(
                collection_name=collection_name,
                query_vectors=query_vectors,
                top_k=5,
                search_params={"nprobe": 10}
            )
            
            assert len(results) == 10
            for result in results:
                assert len(result) <= 5
            
            # Test count
            total_count = await client.count(collection_name)
            assert total_count == batch_size
            
            # Cleanup
            await client.drop_collection(collection_name)
            
        finally:
            await client.disconnect()

    @pytest.mark.asyncio
    async def test_index_operations(self, docker_services, milvus_config, sample_vectors):
        """Test index creation and management."""
        client = AsyncMilvusClient(milvus_config)
        
        try:
            await client.connect()
            
            collection_name = "test_index_ops"
            
            # Create collection without index
            await client.create_collection(
                collection_name=collection_name,
                dimension=128,
                create_index=False
            )
            
            # Insert some data
            await client.insert(
                collection_name=collection_name,
                vectors=sample_vectors
            )
            
            # Create index
            await client.create_index(
                collection_name=collection_name,
                field_name="vector",
                index_type="IVF_FLAT",
                metric_type="L2",
                index_params={"nlist": 128}
            )
            
            # Get index info
            index_info = await client.get_index_info(collection_name)
            assert index_info["index_type"] == "IVF_FLAT"
            assert index_info["metric_type"] == "L2"
            
            # Drop index
            await client.drop_index(collection_name)
            
            # Cleanup
            await client.drop_collection(collection_name)
            
        finally:
            await client.disconnect()

    @pytest.mark.asyncio
    async def test_partition_operations(self, docker_services, milvus_config, sample_vectors):
        """Test partition creation and management."""
        client = AsyncMilvusClient(milvus_config)
        
        try:
            await client.connect()
            
            collection_name = "test_partition_ops"
            
            # Create collection
            await client.create_collection(
                collection_name=collection_name,
                dimension=128,
                index_type="IVF_FLAT",
                metric_type="L2"
            )
            
            # Create partitions
            partition_names = ["partition_1", "partition_2", "partition_3"]
            for partition_name in partition_names:
                await client.create_partition(collection_name, partition_name)
            
            # List partitions
            partitions = await client.list_partitions(collection_name)
            for partition_name in partition_names:
                assert partition_name in partitions
            
            # Insert data into specific partition
            await client.insert(
                collection_name=collection_name,
                vectors=sample_vectors[:5],
                partition_name="partition_1"
            )
            
            await client.insert(
                collection_name=collection_name,
                vectors=sample_vectors[5:],
                partition_name="partition_2"
            )
            
            # Wait for indexing
            await asyncio.sleep(2)
            
            # Search in specific partition
            results = await client.search(
                collection_name=collection_name,
                query_vectors=[sample_vectors[0]],
                top_k=3,
                partition_names=["partition_1"]
            )
            
            assert len(results) == 1
            assert len(results[0]) > 0
            
            # Drop partitions
            for partition_name in partition_names:
                await client.drop_partition(collection_name, partition_name)
            
            # Cleanup
            await client.drop_collection(collection_name)
            
        finally:
            await client.disconnect()

    @pytest.mark.asyncio
    async def test_error_handling(self, docker_services, milvus_config):
        """Test error handling for various failure scenarios."""
        client = AsyncMilvusClient(milvus_config)
        
        try:
            await client.connect()
            
            # Test collection not found error
            with pytest.raises(CollectionError):
                await client.get_collection_info("non_existent_collection")
            
            # Test invalid dimension error
            with pytest.raises(CollectionError):
                await client.create_collection(
                    collection_name="invalid_collection",
                    dimension=0  # Invalid dimension
                )
            
            # Test insert without collection
            with pytest.raises(InsertError):
                await client.insert(
                    collection_name="non_existent_collection",
                    vectors=[[0.1, 0.2, 0.3]]
                )
            
            # Test search without collection
            with pytest.raises(SearchError):
                await client.search(
                    collection_name="non_existent_collection",
                    query_vectors=[[0.1, 0.2, 0.3]],
                    top_k=5
                )
            
        finally:
            await client.disconnect()

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, docker_services, milvus_config):
        """Test concurrent operations on Milvus."""
        client = AsyncMilvusClient(milvus_config)
        
        try:
            await client.connect()
            
            collection_name = "test_concurrent_ops"
            
            # Create collection
            await client.create_collection(
                collection_name=collection_name,
                dimension=128,
                index_type="IVF_FLAT",
                metric_type="L2"
            )
            
            # Concurrent insert operations
            async def insert_batch(batch_id: int):
                vectors = np.random.rand(100, 128).tolist()
                metadata = [{"batch_id": batch_id, "item_id": i} for i in range(100)]
                return await client.insert(
                    collection_name=collection_name,
                    vectors=vectors,
                    metadata=metadata
                )
            
            # Run concurrent inserts
            tasks = [insert_batch(i) for i in range(5)]
            results = await asyncio.gather(*tasks)
            
            # Verify all inserts succeeded
            total_inserted = sum(len(result) for result in results)
            assert total_inserted == 500
            
            # Wait for indexing
            await asyncio.sleep(3)
            
            # Concurrent search operations
            async def search_batch():
                query_vector = np.random.rand(128).tolist()
                return await client.search(
                    collection_name=collection_name,
                    query_vectors=[query_vector],
                    top_k=10
                )
            
            # Run concurrent searches
            search_tasks = [search_batch() for _ in range(10)]
            search_results = await asyncio.gather(*search_tasks)
            
            # Verify all searches succeeded
            assert len(search_results) == 10
            for result in search_results:
                assert len(result) == 1  # One query vector
                assert len(result[0]) <= 10  # Top K results
            
            # Cleanup
            await client.drop_collection(collection_name)
            
        finally:
            await client.disconnect()
