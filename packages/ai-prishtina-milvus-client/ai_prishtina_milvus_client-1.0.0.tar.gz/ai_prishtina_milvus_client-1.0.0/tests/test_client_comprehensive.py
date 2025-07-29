"""
Comprehensive client tests with proper mocking.
"""

import pytest
import asyncio
import numpy as np
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from typing import List, Dict, Any

from ai_prishtina_milvus_client.client import MilvusClient, AsyncMilvusClient
from ai_prishtina_milvus_client.config import MilvusConfig
from ai_prishtina_milvus_client.exceptions import (
    ConnectionError, CollectionError, InsertError, SearchError, MilvusClientError
)


class TestMilvusClientComprehensive:
    """Comprehensive MilvusClient tests."""

    @pytest.fixture
    def milvus_config(self):
        """Create Milvus configuration."""
        return MilvusConfig(
            host="localhost",
            port=19530,
            collection_name="test_collection",
            dim=128,
            index_type="IVF_FLAT",
            metric_type="L2",
            nlist=1024
        )

    @pytest.mark.asyncio
    async def test_client_initialization_and_connection(self, milvus_config):
        """Test client initialization and connection."""
        with patch('ai_prishtina_milvus_client.client.connections') as mock_connections, \
             patch('ai_prishtina_milvus_client.client.Collection') as mock_collection:
            
            # Mock successful connection
            mock_connections.connect.return_value = None
            mock_connections.disconnect.return_value = None
            
            # Mock collection
            mock_collection_instance = MagicMock()
            mock_collection.return_value = mock_collection_instance
            
            # Test synchronous client
            client = MilvusClient(milvus_config)
            
            # Verify connection was established
            mock_connections.connect.assert_called_once()
            
            # Test disconnect
            client.disconnect()
            mock_connections.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_collection_operations(self, milvus_config):
        """Test collection operations."""
        with patch('ai_prishtina_milvus_client.client.connections') as mock_connections, \
             patch('ai_prishtina_milvus_client.client.Collection') as mock_collection, \
             patch('ai_prishtina_milvus_client.client.utility') as mock_utility:
            
            # Mock connections
            mock_connections.connect.return_value = None
            
            # Mock collection
            mock_collection_instance = MagicMock()
            mock_collection.return_value = mock_collection_instance
            mock_collection_instance.create_index.return_value = None
            mock_collection_instance.load.return_value = None
            mock_collection_instance.release.return_value = None
            
            # Mock utility functions
            mock_utility.has_collection.return_value = False
            mock_utility.drop_collection.return_value = None
            mock_utility.list_collections.return_value = ["test_collection"]
            
            client = MilvusClient(milvus_config)
            
            # Test create collection
            client.create_collection()
            mock_collection.assert_called()
            mock_collection_instance.create_index.assert_called()
            
            # Test load collection
            client.load_collection()
            mock_collection_instance.load.assert_called()
            
            # Test release collection
            client.release_collection()
            mock_collection_instance.release.assert_called()
            
            # Test drop collection
            client.drop_collection()
            mock_utility.drop_collection.assert_called()
            
            # Test list collections
            collections = client.list_collections()
            assert collections == ["test_collection"]
            mock_utility.list_collections.assert_called()

    @pytest.mark.asyncio
    async def test_vector_operations(self, milvus_config):
        """Test vector insert, search, and delete operations."""
        with patch('ai_prishtina_milvus_client.client.connections') as mock_connections, \
             patch('ai_prishtina_milvus_client.client.Collection') as mock_collection:
            
            # Mock connections
            mock_connections.connect.return_value = None
            
            # Mock collection
            mock_collection_instance = MagicMock()
            mock_collection.return_value = mock_collection_instance
            
            # Mock insert operation
            mock_insert_result = MagicMock()
            mock_insert_result.primary_keys = [1, 2, 3, 4, 5]
            mock_collection_instance.insert.return_value = mock_insert_result
            
            # Mock search operation
            mock_search_result = [
                [
                    {"id": 1, "distance": 0.1},
                    {"id": 2, "distance": 0.2},
                    {"id": 3, "distance": 0.3}
                ]
            ]
            mock_collection_instance.search.return_value = mock_search_result
            
            # Mock query operation
            mock_query_result = [
                {"id": 1, "vector": [0.1, 0.2, 0.3]},
                {"id": 2, "vector": [0.4, 0.5, 0.6]}
            ]
            mock_collection_instance.query.return_value = mock_query_result
            
            # Mock delete operation
            mock_delete_result = MagicMock()
            mock_delete_result.delete_count = 3
            mock_collection_instance.delete.return_value = mock_delete_result
            
            client = MilvusClient(milvus_config)
            
            # Test vector insertion
            vectors = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]]
            metadata = [{"id": 1}, {"id": 2}, {"id": 3}]
            
            result = client.insert(vectors, metadata)
            assert result == [1, 2, 3, 4, 5]
            mock_collection_instance.insert.assert_called()
            
            # Test vector search
            query_vector = [0.1, 0.2, 0.3]
            search_results = client.search([query_vector], top_k=3)
            assert len(search_results) == 1
            assert len(search_results[0]) == 3
            mock_collection_instance.search.assert_called()
            
            # Test vector query
            query_results = client.query("id in [1, 2]", output_fields=["id", "vector"])
            assert len(query_results) == 2
            mock_collection_instance.query.assert_called()
            
            # Test vector deletion
            delete_count = client.delete("id in [1, 2, 3]")
            assert delete_count == 3
            mock_collection_instance.delete.assert_called()

    @pytest.mark.asyncio
    async def test_error_handling(self, milvus_config):
        """Test error handling in various scenarios."""
        with patch('ai_prishtina_milvus_client.client.connections') as mock_connections:
            
            # Test connection error
            mock_connections.connect.side_effect = Exception("Connection failed")
            
            with pytest.raises(ConnectionError):
                MilvusClient(milvus_config)
            
            # Test collection creation error
            mock_connections.connect.side_effect = None
            mock_connections.connect.return_value = None
            
            with patch('ai_prishtina_milvus_client.client.Collection') as mock_collection:
                mock_collection.side_effect = Exception("Collection creation failed")
                
                client = MilvusClient(milvus_config)
                with pytest.raises(CollectionError):
                    client.create_collection()

    @pytest.mark.asyncio
    async def test_collection_statistics(self, milvus_config):
        """Test collection statistics retrieval."""
        with patch('ai_prishtina_milvus_client.client.connections') as mock_connections, \
             patch('ai_prishtina_milvus_client.client.Collection') as mock_collection:
            
            # Mock connections
            mock_connections.connect.return_value = None
            
            # Mock collection with statistics
            mock_collection_instance = MagicMock()
            mock_collection.return_value = mock_collection_instance
            mock_collection_instance.num_entities = 1000
            mock_collection_instance.schema = MagicMock()
            mock_collection_instance.schema.description = "Test collection"
            
            client = MilvusClient(milvus_config)
            
            # Test get collection statistics
            stats = client.get_collection_stats()
            assert "num_entities" in stats
            assert stats["num_entities"] == 1000

    @pytest.mark.asyncio
    async def test_index_operations(self, milvus_config):
        """Test index operations."""
        with patch('ai_prishtina_milvus_client.client.connections') as mock_connections, \
             patch('ai_prishtina_milvus_client.client.Collection') as mock_collection:
            
            # Mock connections
            mock_connections.connect.return_value = None
            
            # Mock collection
            mock_collection_instance = MagicMock()
            mock_collection.return_value = mock_collection_instance
            mock_collection_instance.create_index.return_value = None
            mock_collection_instance.drop_index.return_value = None
            mock_collection_instance.indexes = [
                MagicMock(field_name="vector", index_type="IVF_FLAT")
            ]
            
            client = MilvusClient(milvus_config)
            
            # Test create index
            client.create_index(
                field_name="vector",
                index_type="IVF_FLAT",
                metric_type="L2",
                params={"nlist": 1024}
            )
            mock_collection_instance.create_index.assert_called()
            
            # Test drop index
            client.drop_index("vector")
            mock_collection_instance.drop_index.assert_called()
            
            # Test list indexes
            indexes = client.list_indexes()
            assert len(indexes) == 1
            assert indexes[0]["field_name"] == "vector"


class TestAsyncMilvusClientComprehensive:
    """Comprehensive AsyncMilvusClient tests."""

    @pytest.fixture
    def milvus_config(self):
        """Create Milvus configuration."""
        return MilvusConfig(
            host="localhost",
            port=19530,
            collection_name="test_collection",
            dim=128,
            index_type="IVF_FLAT",
            metric_type="L2",
            nlist=1024
        )

    @pytest.mark.asyncio
    async def test_async_client_initialization(self, milvus_config):
        """Test async client initialization."""
        with patch('ai_prishtina_milvus_client.client.AsyncMilvusClient._connect') as mock_connect, \
             patch('ai_prishtina_milvus_client.client.AsyncMilvusClient.close') as mock_close:
            
            mock_connect.return_value = None
            mock_close.return_value = None
            
            # Test async client creation
            client = AsyncMilvusClient(milvus_config)
            
            # Test context manager
            async with client as c:
                assert c is client
            
            # Verify close was called
            mock_close.assert_called()

    @pytest.mark.asyncio
    async def test_async_collection_operations(self, milvus_config):
        """Test async collection operations."""
        with patch('ai_prishtina_milvus_client.client.AsyncMilvusClient._connect') as mock_connect, \
             patch('ai_prishtina_milvus_client.client.MilvusClient') as mock_sync_client:
            
            mock_connect.return_value = None
            
            # Mock sync client operations
            mock_sync_instance = MagicMock()
            mock_sync_client.return_value = mock_sync_instance
            mock_sync_instance.create_collection.return_value = None
            mock_sync_instance.list_collections.return_value = ["test_collection"]
            mock_sync_instance.drop_collection.return_value = None
            
            client = AsyncMilvusClient(milvus_config)
            
            # Test async create collection
            await client.create_collection()
            mock_sync_instance.create_collection.assert_called()
            
            # Test async list collections
            collections = await client.list_collections()
            assert collections == ["test_collection"]
            mock_sync_instance.list_collections.assert_called()
            
            # Test async drop collection
            await client.drop_collection("test_collection")
            mock_sync_instance.drop_collection.assert_called()

    @pytest.mark.asyncio
    async def test_async_vector_operations(self, milvus_config):
        """Test async vector operations."""
        with patch('ai_prishtina_milvus_client.client.AsyncMilvusClient._connect') as mock_connect, \
             patch('ai_prishtina_milvus_client.client.MilvusClient') as mock_sync_client:
            
            mock_connect.return_value = None
            
            # Mock sync client operations
            mock_sync_instance = MagicMock()
            mock_sync_client.return_value = mock_sync_instance
            mock_sync_instance.insert.return_value = [1, 2, 3]
            mock_sync_instance.search.return_value = [
                [{"id": 1, "distance": 0.1}, {"id": 2, "distance": 0.2}]
            ]
            mock_sync_instance.query.return_value = [{"id": 1, "vector": [0.1, 0.2]}]
            mock_sync_instance.delete.return_value = 2
            
            client = AsyncMilvusClient(milvus_config)
            
            # Test async insert
            vectors = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
            metadata = [{"id": 1}, {"id": 2}]
            result = await client.insert(vectors, metadata)
            assert result == [1, 2, 3]
            mock_sync_instance.insert.assert_called()
            
            # Test async search
            query_vector = [0.1, 0.2, 0.3]
            search_results = await client.search([query_vector], top_k=2)
            assert len(search_results) == 1
            assert len(search_results[0]) == 2
            mock_sync_instance.search.assert_called()
            
            # Test async query
            query_results = await client.query("id in [1]", output_fields=["id"])
            assert len(query_results) == 1
            mock_sync_instance.query.assert_called()
            
            # Test async delete
            delete_count = await client.delete("id in [1, 2]")
            assert delete_count == 2
            mock_sync_instance.delete.assert_called()

    @pytest.mark.asyncio
    async def test_async_error_handling(self, milvus_config):
        """Test async error handling."""
        with patch('ai_prishtina_milvus_client.client.AsyncMilvusClient._connect') as mock_connect:
            
            # Test connection error
            mock_connect.side_effect = Exception("Async connection failed")
            
            client = AsyncMilvusClient(milvus_config)
            with pytest.raises(Exception):
                await client._connect()

    @pytest.mark.asyncio
    async def test_async_batch_operations(self, milvus_config):
        """Test async batch operations."""
        with patch('ai_prishtina_milvus_client.client.AsyncMilvusClient._connect') as mock_connect, \
             patch('ai_prishtina_milvus_client.client.MilvusClient') as mock_sync_client:
            
            mock_connect.return_value = None
            
            # Mock sync client batch operations
            mock_sync_instance = MagicMock()
            mock_sync_client.return_value = mock_sync_instance
            mock_sync_instance.insert.return_value = list(range(100))
            
            client = AsyncMilvusClient(milvus_config)
            
            # Test large batch insert
            vectors = [np.random.rand(128).tolist() for _ in range(100)]
            metadata = [{"id": i} for i in range(100)]
            
            result = await client.insert(vectors, metadata)
            assert len(result) == 100
            mock_sync_instance.insert.assert_called()

    @pytest.mark.asyncio
    async def test_async_concurrent_operations(self, milvus_config):
        """Test concurrent async operations."""
        with patch('ai_prishtina_milvus_client.client.AsyncMilvusClient._connect') as mock_connect, \
             patch('ai_prishtina_milvus_client.client.MilvusClient') as mock_sync_client:
            
            mock_connect.return_value = None
            
            # Mock sync client operations
            mock_sync_instance = MagicMock()
            mock_sync_client.return_value = mock_sync_instance
            mock_sync_instance.search.return_value = [
                [{"id": 1, "distance": 0.1}]
            ]
            
            client = AsyncMilvusClient(milvus_config)
            
            # Test concurrent searches
            async def search_task(query_id):
                query_vector = np.random.rand(128).tolist()
                return await client.search([query_vector], top_k=1)
            
            # Run multiple concurrent searches
            tasks = [search_task(i) for i in range(10)]
            results = await asyncio.gather(*tasks)
            
            # Verify all searches completed
            assert len(results) == 10
            for result in results:
                assert len(result) == 1
                assert len(result[0]) == 1
            
            # Verify search was called multiple times
            assert mock_sync_instance.search.call_count == 10
