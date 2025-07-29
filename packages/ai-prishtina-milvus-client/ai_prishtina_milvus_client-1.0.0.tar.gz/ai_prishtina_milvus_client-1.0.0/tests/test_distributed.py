"""
Tests for distributed processing module.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import numpy as np
from typing import List, Dict, Any

from ai_prishtina_milvus_client.distributed import (
    CacheConfig,
    DistributedConfig,
    DistributedMilvusClient
)
from ai_prishtina_milvus_client.config import MilvusConfig
from ai_prishtina_milvus_client.exceptions import DistributedError


class TestCacheConfig:
    """Test CacheConfig class."""

    def test_cache_config_creation(self):
        """Test basic cache config creation."""
        config = CacheConfig(
            enabled=True,
            redis_url="redis://localhost:6379",
            ttl=3600,
            max_size=1000
        )

        assert config.enabled is True
        assert config.redis_url == "redis://localhost:6379"
        assert config.ttl == 3600
        assert config.max_size == 1000

    def test_cache_config_defaults(self):
        """Test default values."""
        config = CacheConfig()

        assert config.enabled is True
        assert config.redis_url == "redis://localhost:6379"
        assert config.ttl == 3600
        assert config.max_size == 1000


class TestDistributedConfig:
    """Test DistributedConfig class."""

    def test_distributed_config_creation(self):
        """Test basic distributed config creation."""
        config = DistributedConfig(
            enabled=True,
            num_workers=8,
            chunk_size=2000,
            use_processes=False,
            timeout=600
        )

        assert config.enabled is True
        assert config.num_workers == 8
        assert config.chunk_size == 2000
        assert config.use_processes is False
        assert config.timeout == 600

    def test_distributed_config_validation(self):
        """Test distributed config validation."""
        # Test negative num_workers
        with pytest.raises(ValueError):
            DistributedConfig(
                enabled=True,
                num_workers=-1,
                chunk_size=1000
            )

        # Test zero chunk_size
        with pytest.raises(ValueError):
            DistributedConfig(
                enabled=True,
                num_workers=4,
                chunk_size=0
            )

    def test_distributed_config_defaults(self):
        """Test default values."""
        config = DistributedConfig()

        assert config.enabled is True
        assert config.num_workers >= 1  # Should be at least 1 (os.cpu_count() or 4)
        assert config.chunk_size == 1000
        assert config.use_processes is True
        assert config.timeout == 300


class TestDistributedMilvusClient:
    """Test DistributedMilvusClient class."""

    @pytest.fixture
    def cache_config(self):
        """Create cache configuration."""
        return CacheConfig(
            enabled=True,
            redis_url="redis://localhost:6379",
            ttl=3600,
            max_size=1000
        )

    @pytest.fixture
    def distributed_config(self):
        """Create distributed configuration."""
        return DistributedConfig(
            enabled=True,
            num_workers=4,
            chunk_size=1000,
            use_processes=True,
            timeout=300
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

    def test_distributed_client_creation(self, milvus_config, cache_config, distributed_config):
        """Test distributed client creation."""
        client = DistributedMilvusClient(
            config=milvus_config,
            cache_config=cache_config,
            distributed_config=distributed_config
        )

        assert client.cache_config == cache_config
        assert client.distributed_config == distributed_config
        assert client.redis_client is None  # Not initialized yet

    @pytest.mark.asyncio
    async def test_cache_key_generation(self, milvus_config, cache_config, distributed_config):
        """Test cache key generation."""
        client = DistributedMilvusClient(
            config=milvus_config,
            cache_config=cache_config,
            distributed_config=distributed_config
        )

        # Test cache key generation
        params = {"vectors": [[0.1, 0.2]], "metadata": [{"id": 1}]}
        cache_key = client._get_cache_key("insert", params)

        assert isinstance(cache_key, str)
        assert cache_key.startswith("milvus:insert:")
        assert len(cache_key) > 20  # Should include hash

    @pytest.mark.asyncio
    async def test_redis_initialization(self, milvus_config, cache_config, distributed_config):
        """Test Redis initialization."""
        with patch('aioredis.from_url') as mock_redis:
            mock_redis_instance = AsyncMock()
            mock_redis.return_value = mock_redis_instance

            client = DistributedMilvusClient(
                config=milvus_config,
                cache_config=cache_config,
                distributed_config=distributed_config
            )

            # Initialize Redis
            await client._init_redis()

            assert client.redis_client is not None
            mock_redis.assert_called_once_with(cache_config.redis_url)

    @pytest.mark.asyncio
    async def test_cache_operations(self, milvus_config, cache_config, distributed_config):
        """Test cache set and get operations."""
        with patch('aioredis.from_url') as mock_redis:
            mock_redis_instance = AsyncMock()
            mock_redis_instance.get.return_value = '{"result": "cached_data"}'
            mock_redis_instance.setex.return_value = True
            mock_redis.return_value = mock_redis_instance

            client = DistributedMilvusClient(
                config=milvus_config,
                cache_config=cache_config,
                distributed_config=distributed_config
            )

            await client._init_redis()

            # Test cache set
            await client._set_in_cache("test_key", {"result": "test_data"})
            mock_redis_instance.setex.assert_called()

            # Test cache get
            result = await client._get_from_cache("test_key")
            assert result == {"result": "cached_data"}
            mock_redis_instance.get.assert_called_with("test_key")


    @pytest.mark.asyncio
    async def test_distributed_processing_disabled(self, milvus_config):
        """Test behavior when distributed processing is disabled."""
        distributed_config = DistributedConfig(enabled=False)
        cache_config = CacheConfig(enabled=False)

        client = DistributedMilvusClient(
            config=milvus_config,
            cache_config=cache_config,
            distributed_config=distributed_config
        )

        # Mock the parent class method
        with patch.object(client, '_process_chunk') as mock_process:
            mock_process.return_value = ["result"]

            result = await client._distributed_process(
                data=["test_data"],
                operation="insert"
            )

            # Should call _process_chunk directly when distributed processing is disabled
            mock_process.assert_called_once_with(["test_data"], "insert")
            assert result == ["result"]

    @pytest.mark.asyncio
    async def test_clear_cache(self, milvus_config, cache_config, distributed_config):
        """Test cache clearing."""
        with patch('aioredis.from_url') as mock_redis:
            mock_redis_instance = AsyncMock()
            mock_redis_instance.flushdb.return_value = True
            mock_redis.return_value = mock_redis_instance

            client = DistributedMilvusClient(
                config=milvus_config,
                cache_config=cache_config,
                distributed_config=distributed_config
            )

            await client._init_redis()
            await client.clear_cache()

            # Verify Redis cache was cleared
            mock_redis_instance.flushdb.assert_called_once()




