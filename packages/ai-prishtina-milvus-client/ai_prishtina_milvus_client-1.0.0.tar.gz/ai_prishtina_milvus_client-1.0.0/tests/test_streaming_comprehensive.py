"""
Comprehensive streaming tests.
"""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from typing import List, Dict, Any

from ai_prishtina_milvus_client.streaming import (
    StreamConfig,
    StreamMessage,
    KafkaStreamProcessor
)
from ai_prishtina_milvus_client.config import MilvusConfig
from ai_prishtina_milvus_client.exceptions import StreamingError


class TestStreamingComprehensive:
    """Comprehensive streaming tests."""

    @pytest.fixture
    def stream_config(self):
        """Create stream configuration."""
        return StreamConfig(
            bootstrap_servers="localhost:9092",
            group_id="test_group",
            topics=["test_topic"],
            auto_offset_reset="earliest",
            enable_auto_commit=True,
            max_poll_interval_ms=300000,
            session_timeout_ms=10000,
            max_poll_records=500,
            batch_size=1000,
            num_workers=4
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
    async def test_stream_config_creation(self, stream_config):
        """Test stream configuration creation."""
        assert stream_config.bootstrap_servers == "localhost:9092"
        assert stream_config.group_id == "test_group"
        assert stream_config.topics == ["test_topic"]
        assert stream_config.auto_offset_reset == "earliest"
        assert stream_config.batch_size == 1000
        assert stream_config.max_poll_records == 500
        assert stream_config.enable_auto_commit is True
        assert stream_config.num_workers == 4

    @pytest.mark.asyncio
    async def test_stream_message_creation(self):
        """Test stream message creation."""
        vectors = [[0.1, 0.2, 0.3, 0.4], [0.5, 0.6, 0.7, 0.8]]
        metadata = [
            {"category": "test", "timestamp": "2023-01-01T00:00:00Z"},
            {"category": "test", "timestamp": "2023-01-01T00:01:00Z"}
        ]

        message = StreamMessage(
            vectors=vectors,
            metadata=metadata,
            operation="insert",
            collection="test_collection"
        )

        assert message.vectors == vectors
        assert message.metadata == metadata
        assert message.operation == "insert"
        assert message.collection == "test_collection"

    @pytest.mark.asyncio
    async def test_kafka_stream_processor_initialization(self, stream_config, milvus_config):
        """Test Kafka stream processor initialization."""
        with patch('ai_prishtina_milvus_client.streaming.AsyncMilvusClient') as mock_client:
            mock_client_instance = AsyncMock()
            mock_client.return_value = mock_client_instance

            processor = KafkaStreamProcessor(
                milvus_config=milvus_config,
                stream_config=stream_config
            )

            # Verify initialization
            assert processor.stream_config == stream_config
            assert processor.milvus_config == milvus_config
            assert processor.client is not None

    @pytest.mark.asyncio
    async def test_kafka_stream_processor_produce_message(self, stream_config, milvus_config):
        """Test Kafka stream processor message production."""
        with patch('ai_prishtina_milvus_client.streaming.AIOKafkaProducer') as mock_producer, \
             patch('ai_prishtina_milvus_client.streaming.AsyncMilvusClient') as mock_client:

            # Mock Kafka producer
            mock_producer_instance = AsyncMock()
            mock_producer.return_value = mock_producer_instance

            # Mock Milvus client
            mock_client_instance = AsyncMock()
            mock_client.return_value = mock_client_instance

            processor = KafkaStreamProcessor(
                milvus_config=milvus_config,
                stream_config=stream_config
            )

            # Create test message
            message = StreamMessage(
                vectors=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
                metadata=[{"id": 1}, {"id": 2}],
                operation="insert",
                collection="test_collection"
            )

            # Test message production
            await processor.produce_message("test_topic", message)

            # Verify producer was called
            mock_producer_instance.send.assert_called_once()
