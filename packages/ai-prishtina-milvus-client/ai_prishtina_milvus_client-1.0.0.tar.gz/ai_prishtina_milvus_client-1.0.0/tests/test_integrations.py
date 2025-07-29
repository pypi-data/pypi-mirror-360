"""
Tests for integrations module.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import numpy as np
from typing import List, Dict, Any

from ai_prishtina_milvus_client.integrations import (
    IntegrationConfig,
    BaseIntegration,
    ElasticsearchIntegration,
    RedisIntegration,
    PostgreSQLIntegration,
    IntegrationManager
)
from ai_prishtina_milvus_client.config import MilvusConfig
from ai_prishtina_milvus_client.exceptions import MilvusClientError


class TestIntegrationConfig:
    """Test IntegrationConfig class."""

    def test_integration_config_creation(self):
        """Test basic integration config creation."""
        config = IntegrationConfig(
            integration_type="elasticsearch",
            host="localhost",
            port=9200,
            credentials={"username": "user", "password": "pass"}
        )
        
        assert config.integration_type == "elasticsearch"
        assert config.host == "localhost"
        assert config.port == 9200
        assert config.credentials == {"username": "user", "password": "pass"}

    def test_integration_config_validation(self):
        """Test integration config validation."""
        # Test empty integration type
        with pytest.raises(ValueError):
            IntegrationConfig(
                integration_type="",
                host="localhost",
                port=9200
            )
        
        # Test invalid port
        with pytest.raises(ValueError):
            IntegrationConfig(
                integration_type="elasticsearch",
                host="localhost",
                port=70000  # invalid port
            )

    def test_integration_config_defaults(self):
        """Test default values."""
        config = IntegrationConfig(
            integration_type="elasticsearch",
            host="localhost",
            port=9200
        )
        
        assert config.timeout == 30.0
        assert config.max_retries == 3
        assert config.ssl_enabled is False


class TestBaseIntegration:
    """Test BaseIntegration class."""

    @pytest.fixture
    def integration_config(self):
        """Create integration configuration."""
        return IntegrationConfig(
            integration_type="test",
            host="localhost",
            port=8000
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

    def test_base_integration_creation(self, integration_config, milvus_config):
        """Test base integration creation."""
        integration = BaseIntegration(
            integration_config=integration_config,
            milvus_config=milvus_config
        )
        
        assert integration.integration_config == integration_config
        assert integration.milvus_config == milvus_config
        assert integration.is_connected is False

    @pytest.mark.asyncio
    async def test_base_integration_connect_disconnect(self, integration_config, milvus_config):
        """Test base integration connect and disconnect."""
        integration = BaseIntegration(
            integration_config=integration_config,
            milvus_config=milvus_config
        )
        
        # Test connect (should be implemented by subclasses)
        with pytest.raises(NotImplementedError):
            await integration.connect()
        
        # Test disconnect (should be implemented by subclasses)
        with pytest.raises(NotImplementedError):
            await integration.disconnect()

    @pytest.mark.asyncio
    async def test_base_integration_sync_data(self, integration_config, milvus_config):
        """Test base integration sync data."""
        integration = BaseIntegration(
            integration_config=integration_config,
            milvus_config=milvus_config
        )
        
        # Test sync_data (should be implemented by subclasses)
        with pytest.raises(NotImplementedError):
            await integration.sync_data()


class TestElasticsearchIntegration:
    """Test ElasticsearchIntegration class."""

    @pytest.fixture
    def elasticsearch_config(self):
        """Create Elasticsearch configuration."""
        return IntegrationConfig(
            integration_type="elasticsearch",
            host="localhost",
            port=9200,
            credentials={"username": "user", "password": "pass"}
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

    def test_elasticsearch_integration_creation(self, elasticsearch_config, milvus_config):
        """Test Elasticsearch integration creation."""
        integration = ElasticsearchIntegration(
            integration_config=elasticsearch_config,
            milvus_config=milvus_config
        )
        
        assert integration.integration_config == elasticsearch_config
        assert integration.milvus_config == milvus_config
        assert integration.es_client is None

    @pytest.mark.asyncio
    async def test_elasticsearch_connect(self, elasticsearch_config, milvus_config):
        """Test Elasticsearch connection."""
        with patch('elasticsearch.AsyncElasticsearch') as mock_es:
            mock_es_instance = AsyncMock()
            mock_es_instance.ping.return_value = True
            mock_es.return_value = mock_es_instance
            
            integration = ElasticsearchIntegration(
                integration_config=elasticsearch_config,
                milvus_config=milvus_config
            )
            
            await integration.connect()
            
            assert integration.is_connected is True
            assert integration.es_client is not None
            mock_es_instance.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_elasticsearch_sync_data(self, elasticsearch_config, milvus_config):
        """Test Elasticsearch data synchronization."""
        with patch('elasticsearch.AsyncElasticsearch') as mock_es, \
             patch('ai_prishtina_milvus_client.integrations.AsyncMilvusClient') as mock_milvus:
            
            # Mock Elasticsearch
            mock_es_instance = AsyncMock()
            mock_es_instance.search.return_value = {
                "hits": {
                    "hits": [
                        {
                            "_id": "1",
                            "_source": {
                                "text": "test document",
                                "vector": [0.1, 0.2, 0.3]
                            }
                        }
                    ]
                }
            }
            mock_es.return_value = mock_es_instance
            
            # Mock Milvus
            mock_milvus_instance = AsyncMock()
            mock_milvus.return_value = mock_milvus_instance
            
            integration = ElasticsearchIntegration(
                integration_config=elasticsearch_config,
                milvus_config=milvus_config
            )
            
            await integration.connect()
            await integration.sync_data(index_name="test_index")
            
            # Verify Elasticsearch search was called
            mock_es_instance.search.assert_called()
            
            # Verify Milvus insert was called
            mock_milvus_instance.insert.assert_called()

    @pytest.mark.asyncio
    async def test_elasticsearch_search_integration(self, elasticsearch_config, milvus_config):
        """Test Elasticsearch search integration."""
        with patch('elasticsearch.AsyncElasticsearch') as mock_es:
            mock_es_instance = AsyncMock()
            mock_es_instance.search.return_value = {
                "hits": {
                    "hits": [
                        {
                            "_id": "1",
                            "_source": {"text": "test document"},
                            "_score": 0.9
                        }
                    ]
                }
            }
            mock_es.return_value = mock_es_instance
            
            integration = ElasticsearchIntegration(
                integration_config=elasticsearch_config,
                milvus_config=milvus_config
            )
            
            await integration.connect()
            results = await integration.search(
                index_name="test_index",
                query={"match": {"text": "test"}}
            )
            
            assert len(results) == 1
            assert results[0]["_id"] == "1"
            assert results[0]["_source"]["text"] == "test document"


class TestRedisIntegration:
    """Test RedisIntegration class."""

    @pytest.fixture
    def redis_config(self):
        """Create Redis configuration."""
        return IntegrationConfig(
            integration_type="redis",
            host="localhost",
            port=6379,
            credentials={"password": "pass"}
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

    def test_redis_integration_creation(self, redis_config, milvus_config):
        """Test Redis integration creation."""
        integration = RedisIntegration(
            integration_config=redis_config,
            milvus_config=milvus_config
        )
        
        assert integration.integration_config == redis_config
        assert integration.milvus_config == milvus_config
        assert integration.redis_client is None

    @pytest.mark.asyncio
    async def test_redis_connect(self, redis_config, milvus_config):
        """Test Redis connection."""
        with patch('redis.asyncio.Redis') as mock_redis:
            mock_redis_instance = AsyncMock()
            mock_redis_instance.ping.return_value = True
            mock_redis.return_value = mock_redis_instance
            
            integration = RedisIntegration(
                integration_config=redis_config,
                milvus_config=milvus_config
            )
            
            await integration.connect()
            
            assert integration.is_connected is True
            assert integration.redis_client is not None
            mock_redis_instance.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_redis_cache_operations(self, redis_config, milvus_config):
        """Test Redis cache operations."""
        with patch('redis.asyncio.Redis') as mock_redis:
            mock_redis_instance = AsyncMock()
            mock_redis_instance.get.return_value = b'{"result": "cached"}'
            mock_redis_instance.set.return_value = True
            mock_redis.return_value = mock_redis_instance
            
            integration = RedisIntegration(
                integration_config=redis_config,
                milvus_config=milvus_config
            )
            
            await integration.connect()
            
            # Test cache set
            await integration.cache_set("test_key", {"result": "cached"}, ttl=3600)
            mock_redis_instance.set.assert_called()
            
            # Test cache get
            result = await integration.cache_get("test_key")
            assert result == {"result": "cached"}
            mock_redis_instance.get.assert_called_with("test_key")

    @pytest.mark.asyncio
    async def test_redis_vector_caching(self, redis_config, milvus_config):
        """Test Redis vector caching."""
        with patch('redis.asyncio.Redis') as mock_redis, \
             patch('ai_prishtina_milvus_client.integrations.AsyncMilvusClient') as mock_milvus:
            
            # Mock Redis
            mock_redis_instance = AsyncMock()
            mock_redis_instance.get.return_value = None  # Cache miss
            mock_redis_instance.set.return_value = True
            mock_redis.return_value = mock_redis_instance
            
            # Mock Milvus
            mock_milvus_instance = AsyncMock()
            mock_milvus_instance.search.return_value = [
                [{"id": 1, "distance": 0.1, "entity": {"text": "test"}}]
            ]
            mock_milvus.return_value = mock_milvus_instance
            
            integration = RedisIntegration(
                integration_config=redis_config,
                milvus_config=milvus_config
            )
            
            await integration.connect()
            
            # Search with caching
            query_vector = [0.1, 0.2, 0.3]
            results = await integration.search_with_cache(
                query_vector=query_vector,
                top_k=10,
                cache_ttl=3600
            )
            
            # Verify Milvus search was called (cache miss)
            mock_milvus_instance.search.assert_called()
            
            # Verify result was cached
            mock_redis_instance.set.assert_called()
            
            assert len(results) == 1


class TestPostgreSQLIntegration:
    """Test PostgreSQLIntegration class."""

    @pytest.fixture
    def postgresql_config(self):
        """Create PostgreSQL configuration."""
        return IntegrationConfig(
            integration_type="postgresql",
            host="localhost",
            port=5432,
            credentials={
                "username": "user",
                "password": "pass",
                "database": "testdb"
            }
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

    def test_postgresql_integration_creation(self, postgresql_config, milvus_config):
        """Test PostgreSQL integration creation."""
        integration = PostgreSQLIntegration(
            integration_config=postgresql_config,
            milvus_config=milvus_config
        )
        
        assert integration.integration_config == postgresql_config
        assert integration.milvus_config == milvus_config
        assert integration.pg_pool is None

    @pytest.mark.asyncio
    async def test_postgresql_connect(self, postgresql_config, milvus_config):
        """Test PostgreSQL connection."""
        with patch('asyncpg.create_pool') as mock_create_pool:
            mock_pool = AsyncMock()
            mock_create_pool.return_value = mock_pool
            
            integration = PostgreSQLIntegration(
                integration_config=postgresql_config,
                milvus_config=milvus_config
            )
            
            await integration.connect()
            
            assert integration.is_connected is True
            assert integration.pg_pool is not None
            mock_create_pool.assert_called_once()

    @pytest.mark.asyncio
    async def test_postgresql_sync_data(self, postgresql_config, milvus_config):
        """Test PostgreSQL data synchronization."""
        with patch('asyncpg.create_pool') as mock_create_pool, \
             patch('ai_prishtina_milvus_client.integrations.AsyncMilvusClient') as mock_milvus:
            
            # Mock PostgreSQL
            mock_pool = AsyncMock()
            mock_connection = AsyncMock()
            mock_connection.fetch.return_value = [
                {"id": 1, "text": "test", "vector": [0.1, 0.2, 0.3]}
            ]
            mock_pool.acquire.return_value.__aenter__.return_value = mock_connection
            mock_create_pool.return_value = mock_pool
            
            # Mock Milvus
            mock_milvus_instance = AsyncMock()
            mock_milvus.return_value = mock_milvus_instance
            
            integration = PostgreSQLIntegration(
                integration_config=postgresql_config,
                milvus_config=milvus_config
            )
            
            await integration.connect()
            await integration.sync_data(table_name="test_table")
            
            # Verify PostgreSQL query was executed
            mock_connection.fetch.assert_called()
            
            # Verify Milvus insert was called
            mock_milvus_instance.insert.assert_called()


class TestIntegrationManager:
    """Test IntegrationManager class."""

    @pytest.fixture
    def milvus_config(self):
        """Create Milvus configuration."""
        return MilvusConfig(
            host="localhost",
            port=19530,
            collection_name="test_collection",
            dim=128
        )

    def test_integration_manager_creation(self, milvus_config):
        """Test integration manager creation."""
        manager = IntegrationManager(milvus_config=milvus_config)
        
        assert manager.milvus_config == milvus_config
        assert len(manager.integrations) == 0

    def test_register_integration(self, milvus_config):
        """Test registering integrations."""
        manager = IntegrationManager(milvus_config=milvus_config)
        
        # Create mock integration
        integration_config = IntegrationConfig(
            integration_type="elasticsearch",
            host="localhost",
            port=9200
        )
        
        integration = ElasticsearchIntegration(
            integration_config=integration_config,
            milvus_config=milvus_config
        )
        
        # Register integration
        manager.register_integration("es", integration)
        
        assert "es" in manager.integrations
        assert manager.integrations["es"] == integration

    def test_get_integration(self, milvus_config):
        """Test getting integrations."""
        manager = IntegrationManager(milvus_config=milvus_config)
        
        # Create and register integration
        integration_config = IntegrationConfig(
            integration_type="redis",
            host="localhost",
            port=6379
        )
        
        integration = RedisIntegration(
            integration_config=integration_config,
            milvus_config=milvus_config
        )
        
        manager.register_integration("redis", integration)
        
        # Get integration
        retrieved = manager.get_integration("redis")
        assert retrieved == integration
        
        # Test non-existent integration
        with pytest.raises(KeyError):
            manager.get_integration("nonexistent")

    @pytest.mark.asyncio
    async def test_connect_all_integrations(self, milvus_config):
        """Test connecting all integrations."""
        manager = IntegrationManager(milvus_config=milvus_config)
        
        # Create mock integrations
        integration1 = AsyncMock()
        integration2 = AsyncMock()
        
        manager.register_integration("int1", integration1)
        manager.register_integration("int2", integration2)
        
        # Connect all
        await manager.connect_all()
        
        # Verify all integrations were connected
        integration1.connect.assert_called_once()
        integration2.connect.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_all_integrations(self, milvus_config):
        """Test disconnecting all integrations."""
        manager = IntegrationManager(milvus_config=milvus_config)
        
        # Create mock integrations
        integration1 = AsyncMock()
        integration2 = AsyncMock()
        
        manager.register_integration("int1", integration1)
        manager.register_integration("int2", integration2)
        
        # Disconnect all
        await manager.disconnect_all()
        
        # Verify all integrations were disconnected
        integration1.disconnect.assert_called_once()
        integration2.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_all_integrations(self, milvus_config):
        """Test syncing all integrations."""
        manager = IntegrationManager(milvus_config=milvus_config)
        
        # Create mock integrations
        integration1 = AsyncMock()
        integration2 = AsyncMock()
        
        manager.register_integration("int1", integration1)
        manager.register_integration("int2", integration2)
        
        # Sync all
        await manager.sync_all()
        
        # Verify all integrations were synced
        integration1.sync_data.assert_called_once()
        integration2.sync_data.assert_called_once()
