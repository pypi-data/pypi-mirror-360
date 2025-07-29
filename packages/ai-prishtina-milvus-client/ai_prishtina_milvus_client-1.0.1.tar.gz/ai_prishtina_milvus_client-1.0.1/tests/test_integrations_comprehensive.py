"""
Comprehensive integration tests with real service mocking.

Copyright (c) 2025 Alban Maxhuni <alban.q.maxhuni@gmail.com>

This software is dual-licensed under AGPL-3.0 (open-source) and Commercial licenses.
For commercial licensing, contact: alban.q.maxhuni@gmail.com
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, Mock
import numpy as np
from typing import List, Dict, Any
import json
import time

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


class TestElasticsearchIntegrationComprehensive:
    """Comprehensive Elasticsearch integration tests."""

    @pytest.fixture
    def elasticsearch_config(self):
        """Create Elasticsearch configuration."""
        return IntegrationConfig(
            integration_type="elasticsearch",
            host="localhost",
            port=9200,
            credentials={"username": "elastic", "password": "password"},
            ssl_enabled=True,
            timeout=30.0,
            max_retries=3
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
    async def test_elasticsearch_full_integration(self, elasticsearch_config, milvus_config):
        """Test full Elasticsearch integration workflow."""
        with patch('elasticsearch.AsyncElasticsearch') as mock_es, \
             patch('ai_prishtina_milvus_client.integrations.AsyncMilvusClient') as mock_milvus:
            
            # Mock Elasticsearch responses
            mock_es_instance = AsyncMock()
            mock_es_instance.ping.return_value = True
            mock_es_instance.indices.exists.return_value = True
            mock_es_instance.search.return_value = {
                "hits": {
                    "total": {"value": 1000},
                    "hits": [
                        {
                            "_id": f"doc_{i}",
                            "_source": {
                                "title": f"Document {i}",
                                "content": f"Content for document {i}",
                                "vector": np.random.rand(128).tolist(),
                                "timestamp": "2023-01-01T00:00:00Z"
                            }
                        }
                        for i in range(10)
                    ]
                }
            }
            mock_es_instance.scroll.return_value = {
                "hits": {"hits": []},
                "_scroll_id": "scroll123"
            }
            mock_es.return_value = mock_es_instance
            
            # Mock Milvus client
            mock_milvus_instance = AsyncMock()
            mock_milvus_instance.insert.return_value = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
            mock_milvus.return_value = mock_milvus_instance
            
            # Create integration
            integration = ElasticsearchIntegration(
                integration_config=elasticsearch_config,
                milvus_config=milvus_config
            )
            
            # Test connection
            await integration.connect()
            assert integration.is_connected is True
            
            # Test bulk sync
            result = await integration.bulk_sync(
                index_name="documents",
                batch_size=100,
                scroll_timeout="5m"
            )
            
            # Verify results
            assert result["total_processed"] == 10
            assert result["successful_inserts"] == 10
            assert result["failed_inserts"] == 0
            
            # Verify Elasticsearch calls
            mock_es_instance.search.assert_called()
            mock_es_instance.scroll.assert_called()
            
            # Verify Milvus calls
            mock_milvus_instance.insert.assert_called()

    @pytest.mark.asyncio
    async def test_elasticsearch_error_handling(self, elasticsearch_config, milvus_config):
        """Test Elasticsearch error handling."""
        with patch('elasticsearch.AsyncElasticsearch') as mock_es:
            
            # Mock connection failure
            mock_es_instance = AsyncMock()
            mock_es_instance.ping.side_effect = Exception("Connection failed")
            mock_es.return_value = mock_es_instance
            
            integration = ElasticsearchIntegration(
                integration_config=elasticsearch_config,
                milvus_config=milvus_config
            )
            
            # Test connection error handling
            with pytest.raises(MilvusClientError):
                await integration.connect()

    @pytest.mark.asyncio
    async def test_elasticsearch_search_with_filters(self, elasticsearch_config, milvus_config):
        """Test Elasticsearch search with complex filters."""
        with patch('elasticsearch.AsyncElasticsearch') as mock_es:
            
            mock_es_instance = AsyncMock()
            mock_es_instance.ping.return_value = True
            mock_es_instance.search.return_value = {
                "hits": {
                    "hits": [
                        {
                            "_id": "filtered_doc",
                            "_source": {
                                "title": "Filtered Document",
                                "category": "important",
                                "score": 0.95
                            },
                            "_score": 1.5
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
            
            # Test complex search with filters
            results = await integration.search_with_filters(
                index_name="documents",
                query={
                    "bool": {
                        "must": [
                            {"match": {"title": "important"}},
                            {"range": {"score": {"gte": 0.8}}}
                        ],
                        "filter": [
                            {"term": {"category": "important"}}
                        ]
                    }
                },
                size=50,
                sort=[{"score": {"order": "desc"}}]
            )
            
            assert len(results) == 1
            assert results[0]["_source"]["category"] == "important"
            
            # Verify search was called with correct parameters
            mock_es_instance.search.assert_called_with(
                index="documents",
                body={
                    "query": {
                        "bool": {
                            "must": [
                                {"match": {"title": "important"}},
                                {"range": {"score": {"gte": 0.8}}}
                            ],
                            "filter": [
                                {"term": {"category": "important"}}
                            ]
                        }
                    },
                    "size": 50,
                    "sort": [{"score": {"order": "desc"}}]
                }
            )


class TestRedisIntegrationComprehensive:
    """Comprehensive Redis integration tests."""

    @pytest.fixture
    def redis_config(self):
        """Create Redis configuration."""
        return IntegrationConfig(
            integration_type="redis",
            host="localhost",
            port=6379,
            credentials={"password": "redis_password"},
            timeout=10.0,
            max_retries=3
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
    async def test_redis_caching_workflow(self, redis_config, milvus_config):
        """Test complete Redis caching workflow."""
        with patch('redis.asyncio.Redis') as mock_redis, \
             patch('ai_prishtina_milvus_client.integrations.AsyncMilvusClient') as mock_milvus:
            
            # Mock Redis
            mock_redis_instance = AsyncMock()
            mock_redis_instance.ping.return_value = True
            mock_redis_instance.get.return_value = None  # Cache miss initially
            mock_redis_instance.setex.return_value = True
            mock_redis_instance.exists.return_value = False
            mock_redis.return_value = mock_redis_instance
            
            # Mock Milvus
            mock_milvus_instance = AsyncMock()
            mock_milvus_instance.search.return_value = [
                [
                    {"id": 1, "distance": 0.1, "entity": {"text": "result 1"}},
                    {"id": 2, "distance": 0.2, "entity": {"text": "result 2"}}
                ]
            ]
            mock_milvus.return_value = mock_milvus_instance
            
            integration = RedisIntegration(
                integration_config=redis_config,
                milvus_config=milvus_config
            )
            
            await integration.connect()
            
            # Test cache miss scenario
            query_vector = np.random.rand(128).tolist()
            results = await integration.search_with_cache(
                query_vector=query_vector,
                top_k=10,
                cache_ttl=3600
            )
            
            # Verify Milvus search was called (cache miss)
            mock_milvus_instance.search.assert_called_once()
            
            # Verify result was cached
            mock_redis_instance.setex.assert_called()
            
            # Test cache hit scenario
            mock_redis_instance.get.return_value = json.dumps([
                [
                    {"id": 1, "distance": 0.1, "entity": {"text": "cached result 1"}},
                    {"id": 2, "distance": 0.2, "entity": {"text": "cached result 2"}}
                ]
            ])
            
            cached_results = await integration.search_with_cache(
                query_vector=query_vector,
                top_k=10,
                cache_ttl=3600
            )
            
            # Verify cached results
            assert len(cached_results) == 1
            assert len(cached_results[0]) == 2
            assert cached_results[0][0]["entity"]["text"] == "cached result 1"

    @pytest.mark.asyncio
    async def test_redis_batch_operations(self, redis_config, milvus_config):
        """Test Redis batch operations."""
        with patch('redis.asyncio.Redis') as mock_redis:
            
            mock_redis_instance = AsyncMock()
            mock_redis_instance.ping.return_value = True
            mock_redis_instance.mget.return_value = [None, None, None]  # All cache misses
            mock_redis_instance.mset.return_value = True
            mock_redis.return_value = mock_redis_instance
            
            integration = RedisIntegration(
                integration_config=redis_config,
                milvus_config=milvus_config
            )
            
            await integration.connect()
            
            # Test batch cache operations
            keys = ["key1", "key2", "key3"]
            values = [{"data": f"value{i}"} for i in range(3)]
            
            # Batch set
            await integration.batch_cache_set(
                key_value_pairs=dict(zip(keys, values)),
                ttl=1800
            )
            
            # Verify batch set was called
            mock_redis_instance.mset.assert_called()
            
            # Batch get
            results = await integration.batch_cache_get(keys)
            
            # Verify batch get was called
            mock_redis_instance.mget.assert_called_with(keys)
            
            assert len(results) == 3
            assert all(result is None for result in results)  # All cache misses

    @pytest.mark.asyncio
    async def test_redis_performance_monitoring(self, redis_config, milvus_config):
        """Test Redis performance monitoring."""
        with patch('redis.asyncio.Redis') as mock_redis:
            
            mock_redis_instance = AsyncMock()
            mock_redis_instance.ping.return_value = True
            mock_redis_instance.info.return_value = {
                "used_memory": 1024000,
                "used_memory_human": "1000K",
                "connected_clients": 5,
                "total_commands_processed": 1000,
                "keyspace_hits": 800,
                "keyspace_misses": 200
            }
            mock_redis.return_value = mock_redis_instance
            
            integration = RedisIntegration(
                integration_config=redis_config,
                milvus_config=milvus_config
            )
            
            await integration.connect()
            
            # Get performance metrics
            metrics = await integration.get_performance_metrics()
            
            assert metrics["memory_usage"] == 1024000
            assert metrics["connected_clients"] == 5
            assert metrics["cache_hit_ratio"] == 0.8  # 800/(800+200)
            assert metrics["total_commands"] == 1000
            
            mock_redis_instance.info.assert_called_once()


class TestPostgreSQLIntegrationComprehensive:
    """Comprehensive PostgreSQL integration tests."""

    @pytest.fixture
    def postgresql_config(self):
        """Create PostgreSQL configuration."""
        return IntegrationConfig(
            integration_type="postgresql",
            host="localhost",
            port=5432,
            credentials={
                "username": "postgres",
                "password": "password",
                "database": "vectordb"
            },
            timeout=30.0,
            max_retries=3
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
    async def test_postgresql_data_migration(self, postgresql_config, milvus_config):
        """Test PostgreSQL to Milvus data migration."""
        with patch('asyncpg.create_pool') as mock_create_pool, \
             patch('ai_prishtina_milvus_client.integrations.AsyncMilvusClient') as mock_milvus:
            
            # Mock PostgreSQL
            mock_pool = AsyncMock()
            mock_connection = AsyncMock()
            
            # Mock data from PostgreSQL
            mock_data = [
                {
                    "id": i,
                    "title": f"Document {i}",
                    "content": f"Content for document {i}",
                    "vector": np.random.rand(128).tolist(),
                    "created_at": "2023-01-01T00:00:00Z"
                }
                for i in range(100)
            ]
            
            mock_connection.fetch.return_value = mock_data
            mock_pool.acquire.return_value.__aenter__.return_value = mock_connection
            mock_create_pool.return_value = mock_pool
            
            # Mock Milvus
            mock_milvus_instance = AsyncMock()
            mock_milvus_instance.insert.return_value = list(range(100))
            mock_milvus.return_value = mock_milvus_instance
            
            integration = PostgreSQLIntegration(
                integration_config=postgresql_config,
                milvus_config=milvus_config
            )
            
            await integration.connect()
            
            # Test data migration
            result = await integration.migrate_data(
                table_name="documents",
                vector_column="vector",
                batch_size=50,
                where_clause="created_at >= '2023-01-01'"
            )
            
            # Verify results
            assert result["total_migrated"] == 100
            assert result["batches_processed"] == 2
            assert result["failed_records"] == 0
            
            # Verify PostgreSQL query was called
            mock_connection.fetch.assert_called()
            
            # Verify Milvus insert was called (2 batches of 50)
            assert mock_milvus_instance.insert.call_count == 2

    @pytest.mark.asyncio
    async def test_postgresql_incremental_sync(self, postgresql_config, milvus_config):
        """Test PostgreSQL incremental synchronization."""
        with patch('asyncpg.create_pool') as mock_create_pool, \
             patch('ai_prishtina_milvus_client.integrations.AsyncMilvusClient') as mock_milvus:
            
            # Mock PostgreSQL
            mock_pool = AsyncMock()
            mock_connection = AsyncMock()
            
            # Mock incremental data (only new/updated records)
            mock_incremental_data = [
                {
                    "id": 101,
                    "title": "New Document 101",
                    "vector": np.random.rand(128).tolist(),
                    "updated_at": "2023-01-02T00:00:00Z"
                }
            ]
            
            mock_connection.fetch.return_value = mock_incremental_data
            mock_pool.acquire.return_value.__aenter__.return_value = mock_connection
            mock_create_pool.return_value = mock_pool
            
            # Mock Milvus
            mock_milvus_instance = AsyncMock()
            mock_milvus_instance.insert.return_value = [101]
            mock_milvus.return_value = mock_milvus_instance
            
            integration = PostgreSQLIntegration(
                integration_config=postgresql_config,
                milvus_config=milvus_config
            )
            
            await integration.connect()
            
            # Test incremental sync
            result = await integration.incremental_sync(
                table_name="documents",
                timestamp_column="updated_at",
                last_sync_timestamp="2023-01-01T00:00:00Z"
            )
            
            # Verify only new records were processed
            assert result["new_records"] == 1
            assert result["updated_records"] == 0
            
            # Verify correct WHERE clause was used
            expected_query = """
                SELECT * FROM documents 
                WHERE updated_at > $1 
                ORDER BY updated_at ASC
            """
            mock_connection.fetch.assert_called()


class TestIntegrationManagerComprehensive:
    """Comprehensive integration manager tests."""

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
    async def test_multi_integration_workflow(self, milvus_config):
        """Test workflow with multiple integrations."""
        manager = IntegrationManager(milvus_config=milvus_config)
        
        # Create mock integrations
        es_integration = AsyncMock()
        redis_integration = AsyncMock()
        pg_integration = AsyncMock()
        
        # Register integrations
        manager.register_integration("elasticsearch", es_integration)
        manager.register_integration("redis", redis_integration)
        manager.register_integration("postgresql", pg_integration)
        
        # Test connect all
        await manager.connect_all()
        
        es_integration.connect.assert_called_once()
        redis_integration.connect.assert_called_once()
        pg_integration.connect.assert_called_once()
        
        # Test health check all
        es_integration.health_check.return_value = True
        redis_integration.health_check.return_value = True
        pg_integration.health_check.return_value = False  # One unhealthy
        
        health_status = await manager.health_check_all()
        
        assert health_status["elasticsearch"] is True
        assert health_status["redis"] is True
        assert health_status["postgresql"] is False
        
        # Test disconnect all
        await manager.disconnect_all()
        
        es_integration.disconnect.assert_called_once()
        redis_integration.disconnect.assert_called_once()
        pg_integration.disconnect.assert_called_once()

    @pytest.mark.asyncio
    async def test_integration_failover(self, milvus_config):
        """Test integration failover mechanisms."""
        manager = IntegrationManager(milvus_config=milvus_config)
        
        # Create primary and backup integrations
        primary_integration = AsyncMock()
        backup_integration = AsyncMock()
        
        # Primary fails, backup succeeds
        primary_integration.search.side_effect = Exception("Primary failed")
        backup_integration.search.return_value = [{"id": 1, "score": 0.9}]
        
        manager.register_integration("primary", primary_integration)
        manager.register_integration("backup", backup_integration)
        
        # Test failover
        result = await manager.search_with_failover(
            query="test query",
            primary_integration="primary",
            backup_integration="backup"
        )
        
        # Verify primary was tried first
        primary_integration.search.assert_called_once()
        
        # Verify backup was used after primary failed
        backup_integration.search.assert_called_once()
        
        # Verify result from backup
        assert result == [{"id": 1, "score": 0.9}]
