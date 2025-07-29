"""
Tests for streaming module.

Copyright (c) 2025 Alban Maxhuni <alban.q.maxhuni@gmail.com>

This software is dual-licensed under AGPL-3.0 (open-source) and Commercial licenses.
For commercial licensing, contact: alban.q.maxhuni@gmail.com
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import json
from typing import Dict, Any

from ai_prishtina_milvus_client.streaming import (
    StreamConfig,
    StreamMessage,
    KafkaStreamProcessor
)
from ai_prishtina_milvus_client.config import MilvusConfig
from ai_prishtina_milvus_client.exceptions import StreamingError


class TestStreamConfig:
    """Test StreamConfig class."""

    def test_stream_config_creation(self):
        """Test basic stream config creation."""
        config = StreamConfig(
            bootstrap_servers="localhost:9092",
            group_id="test_group",
            topics=["test_topic"]
        )

        assert config.bootstrap_servers == "localhost:9092"
        assert config.topics == ["test_topic"]
        assert config.group_id == "test_group"
        assert config.auto_offset_reset == "earliest"  # default

    def test_stream_config_validation(self):
        """Test stream config validation."""
        # Test empty topics
        with pytest.raises(ValueError):
            StreamConfig(
                bootstrap_servers="localhost:9092",
                topics=[],
                group_id="test_group"
            )

        # Test empty group_id
        with pytest.raises(ValueError):
            StreamConfig(
                bootstrap_servers="localhost:9092",
                topics=["test_topic"],
                group_id=""
            )

    def test_stream_config_defaults(self):
        """Test default values."""
        config = StreamConfig(
            bootstrap_servers="localhost:9092",
            topics=["test_topic"],
            group_id="test_group"
        )

        assert config.auto_offset_reset == "earliest"
        assert config.enable_auto_commit is True
        assert config.max_poll_records == 500


class TestStreamMessage:
    """Test StreamMessage class."""

    def test_stream_message_creation(self):
        """Test stream message creation."""
        vectors = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        metadata = [{"id": 1, "text": "test1"}, {"id": 2, "text": "test2"}]
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

    def test_stream_message_defaults(self):
        """Test message defaults."""
        vectors = [[0.1, 0.2, 0.3]]
        message = StreamMessage(vectors=vectors)

        assert message.vectors == vectors
        assert message.metadata is None
        assert message.operation == "insert"
        assert message.collection == "default"


class TestKafkaStreamProcessor:
    """Test KafkaStreamProcessor class."""

    @pytest.fixture
    def stream_config(self):
        """Create stream configuration."""
        return StreamConfig(
            bootstrap_servers="localhost:9092",
            topics=["test_topic"],
            group_id="test_group"
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

    def test_processor_creation(self, stream_config, milvus_config):
        """Test processor creation."""
        processor = KafkaStreamProcessor(
            milvus_config=milvus_config,
            stream_config=stream_config
        )

        assert processor.stream_config == stream_config
        assert processor.milvus_config == milvus_config

    @pytest.mark.asyncio
    async def test_processor_start_stop(self, stream_config, milvus_config):
        """Test processor start and stop."""
        with patch('ai_prishtina_milvus_client.streaming.AIOKafkaConsumer') as mock_consumer, \
             patch('ai_prishtina_milvus_client.streaming.AIOKafkaProducer') as mock_producer:
            
            # Mock consumer and producer
            mock_consumer_instance = AsyncMock()
            mock_producer_instance = AsyncMock()
            mock_consumer.return_value = mock_consumer_instance
            mock_producer.return_value = mock_producer_instance
            
            processor = KafkaStreamProcessor(
                stream_config=stream_config,
                milvus_config=milvus_config
            )
            
            # Test start
            await processor.start()
            assert processor.consumer is not None
            assert processor.producer is not None
            mock_consumer_instance.start.assert_called_once()
            mock_producer_instance.start.assert_called_once()
            
            # Test stop
            await processor.stop()
            mock_consumer_instance.stop.assert_called_once()
            mock_producer_instance.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_message_processing(self, stream_config, milvus_config):
        """Test message processing."""
        with patch('ai_prishtina_milvus_client.streaming.AIOKafkaConsumer') as mock_consumer, \
             patch('ai_prishtina_milvus_client.streaming.AIOKafkaProducer') as mock_producer, \
             patch('ai_prishtina_milvus_client.streaming.AsyncMilvusClient') as mock_client:
            
            # Mock Kafka message
            kafka_msg = MagicMock()
            kafka_msg.topic = "test_topic"
            kafka_msg.partition = 0
            kafka_msg.offset = 123
            kafka_msg.key = b"test_key"
            kafka_msg.value = b'{"id": 1, "text": "test", "vector": [0.1, 0.2, 0.3]}'
            kafka_msg.timestamp = 1234567890
            
            # Mock consumer
            mock_consumer_instance = AsyncMock()
            mock_consumer_instance.__aiter__.return_value = [kafka_msg]
            mock_consumer.return_value = mock_consumer_instance
            
            # Mock producer
            mock_producer_instance = AsyncMock()
            mock_producer.return_value = mock_producer_instance
            
            # Mock Milvus client
            mock_client_instance = AsyncMock()
            mock_client.return_value = mock_client_instance
            
            processor = KafkaStreamProcessor(
                stream_config=stream_config,
                milvus_config=milvus_config
            )
            
            # Mock message handler
            handler = AsyncMock()
            processor.set_message_handler(handler)
            
            await processor.start()
            
            # Process one message
            await processor.process_messages(max_messages=1)
            
            # Verify handler was called
            handler.assert_called_once()
            call_args = handler.call_args[0][0]
            assert isinstance(call_args, StreamMessage)
            assert call_args.topic == "test_topic"

    @pytest.mark.asyncio
    async def test_send_message(self, stream_config, milvus_config):
        """Test sending messages."""
        with patch('ai_prishtina_milvus_client.streaming.AIOKafkaProducer') as mock_producer:
            
            mock_producer_instance = AsyncMock()
            mock_producer.return_value = mock_producer_instance
            
            processor = KafkaStreamProcessor(
                stream_config=stream_config,
                milvus_config=milvus_config
            )
            
            await processor.start()
            
            # Send message
            data = {"id": 1, "text": "test"}
            await processor.send_message("test_topic", data, key="test_key")
            
            # Verify producer.send was called
            mock_producer_instance.send.assert_called_once()

    @pytest.mark.asyncio
    async def test_error_handling(self, stream_config, milvus_config):
        """Test error handling."""
        with patch('ai_prishtina_milvus_client.streaming.AIOKafkaConsumer') as mock_consumer:
            
            # Mock consumer that raises exception
            mock_consumer_instance = AsyncMock()
            mock_consumer_instance.start.side_effect = Exception("Connection failed")
            mock_consumer.return_value = mock_consumer_instance
            
            processor = KafkaStreamProcessor(
                stream_config=stream_config,
                milvus_config=milvus_config
            )
            
            # Test that StreamingError is raised
            with pytest.raises(StreamingError):
                await processor.start()

    @pytest.mark.asyncio
    async def test_message_handler_error(self, stream_config, milvus_config):
        """Test message handler error handling."""
        with patch('ai_prishtina_milvus_client.streaming.AIOKafkaConsumer') as mock_consumer, \
             patch('ai_prishtina_milvus_client.streaming.AIOKafkaProducer') as mock_producer:
            
            # Mock Kafka message
            kafka_msg = MagicMock()
            kafka_msg.topic = "test_topic"
            kafka_msg.partition = 0
            kafka_msg.offset = 123
            kafka_msg.value = b'{"id": 1, "text": "test"}'
            
            # Mock consumer
            mock_consumer_instance = AsyncMock()
            mock_consumer_instance.__aiter__.return_value = [kafka_msg]
            mock_consumer.return_value = mock_consumer_instance
            
            # Mock producer
            mock_producer_instance = AsyncMock()
            mock_producer.return_value = mock_producer_instance
            
            processor = KafkaStreamProcessor(
                stream_config=stream_config,
                milvus_config=milvus_config
            )
            
            # Mock message handler that raises exception
            handler = AsyncMock()
            handler.side_effect = Exception("Handler error")
            processor.set_message_handler(handler)
            
            await processor.start()
            
            # Process message - should handle error gracefully
            await processor.process_messages(max_messages=1)
            
            # Handler should have been called despite error
            handler.assert_called_once()

    def test_message_handler_setting(self, stream_config, milvus_config):
        """Test setting message handler."""
        processor = KafkaStreamProcessor(
            stream_config=stream_config,
            milvus_config=milvus_config
        )
        
        async def test_handler(message):
            pass
        
        processor.set_message_handler(test_handler)
        assert processor.message_handler == test_handler

    @pytest.mark.asyncio
    async def test_context_manager(self, stream_config, milvus_config):
        """Test using processor as context manager."""
        with patch('ai_prishtina_milvus_client.streaming.AIOKafkaConsumer') as mock_consumer, \
             patch('ai_prishtina_milvus_client.streaming.AIOKafkaProducer') as mock_producer:
            
            mock_consumer_instance = AsyncMock()
            mock_producer_instance = AsyncMock()
            mock_consumer.return_value = mock_consumer_instance
            mock_producer.return_value = mock_producer_instance
            
            async with KafkaStreamProcessor(stream_config, milvus_config) as processor:
                assert processor.consumer is not None
                assert processor.producer is not None
            
            # Verify stop was called
            mock_consumer_instance.stop.assert_called_once()
            mock_producer_instance.stop.assert_called_once()

    @pytest.mark.asyncio
    async def test_batch_processing(self, stream_config, milvus_config):
        """Test batch message processing."""
        with patch('ai_prishtina_milvus_client.streaming.AIOKafkaConsumer') as mock_consumer, \
             patch('ai_prishtina_milvus_client.streaming.AIOKafkaProducer') as mock_producer:
            
            # Create multiple mock messages
            messages = []
            for i in range(5):
                msg = MagicMock()
                msg.topic = "test_topic"
                msg.partition = 0
                msg.offset = i
                msg.value = f'{{"id": {i}, "text": "test_{i}"}}'.encode()
                messages.append(msg)
            
            # Mock consumer
            mock_consumer_instance = AsyncMock()
            mock_consumer_instance.__aiter__.return_value = messages
            mock_consumer.return_value = mock_consumer_instance
            
            # Mock producer
            mock_producer_instance = AsyncMock()
            mock_producer.return_value = mock_producer_instance
            
            processor = KafkaStreamProcessor(
                stream_config=stream_config,
                milvus_config=milvus_config
            )
            
            # Mock batch handler
            batch_handler = AsyncMock()
            processor.set_batch_handler(batch_handler, batch_size=3)
            
            await processor.start()
            await processor.process_messages(max_messages=5)
            
            # Should be called twice: once for batch of 3, once for batch of 2
            assert batch_handler.call_count == 2
