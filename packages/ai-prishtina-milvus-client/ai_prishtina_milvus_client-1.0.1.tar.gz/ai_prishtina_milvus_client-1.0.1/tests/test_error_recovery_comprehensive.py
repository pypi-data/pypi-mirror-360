"""
Comprehensive error recovery tests.

Copyright (c) 2025 Alban Maxhuni <alban.q.maxhuni@gmail.com>

This software is dual-licensed under AGPL-3.0 (open-source) and Commercial licenses.
For commercial licensing, contact: alban.q.maxhuni@gmail.com
"""

import pytest
import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from typing import List, Dict, Any

from ai_prishtina_milvus_client.error_recovery import (
    ErrorRecovery,
    RetryConfig
)
from ai_prishtina_milvus_client.config import MilvusConfig
from ai_prishtina_milvus_client.exceptions import (
    ErrorRecoveryError, ConnectionError, MilvusClientError
)


class TestErrorRecoveryComprehensive:
    """Comprehensive error recovery tests."""

    @pytest.fixture
    def retry_config(self):
        """Create retry configuration."""
        return RetryConfig(
            max_attempts=3,
            initial_delay=1.0,
            max_delay=10.0,
            backoff_factor=2.0,
            retry_on_exceptions=[ConnectionError, Exception]
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
    async def test_error_recovery_initialization(self, retry_config, milvus_config):
        """Test error recovery initialization."""
        with patch('ai_prishtina_milvus_client.error_recovery.AsyncMilvusClient') as mock_client:
            mock_client_instance = AsyncMock()
            mock_client.return_value = mock_client_instance

            recovery = ErrorRecovery(
                milvus_config=milvus_config,
                retry_config=retry_config
            )

            # Verify initialization
            assert recovery.milvus_config == milvus_config
            assert recovery.retry_config == retry_config
            assert recovery.client is not None

            # Test configuration
            assert recovery.retry_config.max_attempts == 3
            assert recovery.retry_config.initial_delay == 1.0
            assert recovery.retry_config.backoff_factor == 2.0

    @pytest.mark.asyncio
    async def test_retry_operation_success(self, retry_config, milvus_config):
        """Test successful retry operation."""
        with patch('ai_prishtina_milvus_client.error_recovery.AsyncMilvusClient') as mock_client:
            mock_client_instance = AsyncMock()
            mock_client.return_value = mock_client_instance

            recovery = ErrorRecovery(
                milvus_config=milvus_config,
                retry_config=retry_config
            )

            # Test successful operation (no retries needed)
            async def successful_operation():
                return "success"

            result = await recovery.retry_operation(successful_operation)
            assert result == "success"

    @pytest.mark.asyncio
    async def test_retry_with_failures(self, retry_config, milvus_config):
        """Test retry behavior with failures."""
        with patch('ai_prishtina_milvus_client.error_recovery.AsyncMilvusClient') as mock_client:
            mock_client_instance = AsyncMock()
            mock_client.return_value = mock_client_instance

            recovery = ErrorRecovery(
                milvus_config=milvus_config,
                retry_config=retry_config
            )

            # Test operation that fails then succeeds
            call_count = 0

            async def failing_operation():
                nonlocal call_count
                call_count += 1
                if call_count < 3:
                    raise ConnectionError("Connection failed")
                return "success"

            result = await recovery.retry_operation(failing_operation)

            # Should succeed after retries
            assert result == "success"
            assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_max_attempts(self, retry_config, milvus_config):
        """Test retry with max attempts exceeded."""
        with patch('ai_prishtina_milvus_client.error_recovery.AsyncMilvusClient') as mock_client:
            mock_client_instance = AsyncMock()
            mock_client.return_value = mock_client_instance

            recovery = ErrorRecovery(
                milvus_config=milvus_config,
                retry_config=retry_config
            )

            # Test operation that always fails
            call_count = 0

            async def always_failing_operation():
                nonlocal call_count
                call_count += 1
                raise ConnectionError("Always fails")

            with pytest.raises(ConnectionError):
                await recovery.retry_operation(always_failing_operation)

            # Should have tried max_attempts times
            assert call_count == retry_config.max_attempts

    @pytest.mark.asyncio
    async def test_retry_config_validation(self, retry_config, milvus_config):
        """Test retry configuration validation."""
        # Test valid configuration
        assert retry_config.max_attempts == 3
        assert retry_config.initial_delay == 1.0
        assert retry_config.max_delay == 10.0
        assert retry_config.backoff_factor == 2.0
        assert ConnectionError in retry_config.retry_on_exceptions

        # Test custom configuration
        custom_config = RetryConfig(
            max_attempts=5,
            initial_delay=0.5,
            max_delay=20.0,
            backoff_factor=1.5,
            retry_on_exceptions=[ValueError, RuntimeError]
        )

        assert custom_config.max_attempts == 5
        assert custom_config.initial_delay == 0.5
        assert custom_config.max_delay == 20.0
        assert custom_config.backoff_factor == 1.5
        assert ValueError in custom_config.retry_on_exceptions
        assert RuntimeError in custom_config.retry_on_exceptions
