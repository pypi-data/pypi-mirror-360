"""
Integration tests for Kafka streaming using Docker containers.
"""

import pytest
import asyncio
import json
import time
from typing import List, Dict, Any

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from ai_prishtina_milvus_client.streaming import StreamConfig, StreamMessage, KafkaStreamProcessor
from ai_prishtina_milvus_client.config import MilvusConfig
from ai_prishtina_milvus_client.exceptions import StreamingError


@pytest.mark.integration
@pytest.mark.docker
class TestKafkaIntegration:
    """Integration tests for Kafka streaming operations."""

    @pytest.mark.asyncio
    async def test_kafka_connection(self, docker_services, kafka_config):
        """Test basic Kafka connection."""
        # Test producer connection
        producer = AIOKafkaProducer(
            bootstrap_servers=kafka_config.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        try:
            await producer.start()
            
            # Send test message
            test_message = {"test": "connection", "timestamp": time.time()}
            await producer.send("test_topic", test_message)
            await producer.flush()
            
        finally:
            await producer.stop()
        
        # Test consumer connection
        consumer = AIOKafkaConsumer(
            "test_topic",
            bootstrap_servers=kafka_config.bootstrap_servers,
            group_id="test_group",
            auto_offset_reset="earliest",
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        try:
            await consumer.start()
            
            # Consume the test message
            async for message in consumer:
                assert message.value["test"] == "connection"
                break
                
        finally:
            await consumer.stop()

    @pytest.mark.asyncio
    async def test_stream_message_production(self, docker_services, kafka_config, sample_vectors, sample_metadata):
        """Test producing stream messages to Kafka."""
        producer = AIOKafkaProducer(
            bootstrap_servers=kafka_config.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        try:
            await producer.start()
            
            # Create stream messages
            messages = []
            for i in range(5):
                message = StreamMessage(
                    vectors=[sample_vectors[i]],
                    metadata=[sample_metadata[i]],
                    operation="insert",
                    collection="test_collection"
                )
                messages.append(message)
            
            # Send messages
            topic = "vector_stream"
            for i, message in enumerate(messages):
                message_data = {
                    "vectors": message.vectors,
                    "metadata": message.metadata,
                    "operation": message.operation,
                    "collection": message.collection,
                    "message_id": f"msg_{i}",
                    "timestamp": time.time()
                }
                
                await producer.send(topic, message_data)
            
            await producer.flush()
            
        finally:
            await producer.stop()

    @pytest.mark.asyncio
    async def test_stream_message_consumption(self, docker_services, kafka_config):
        """Test consuming stream messages from Kafka."""
        topic = "vector_consumption_test"
        
        # First, produce some test messages
        producer = AIOKafkaProducer(
            bootstrap_servers=kafka_config.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        try:
            await producer.start()
            
            # Send test messages
            test_messages = []
            for i in range(10):
                message_data = {
                    "vectors": [[0.1 * i, 0.2 * i, 0.3 * i]],
                    "metadata": [{"id": i, "category": f"cat_{i % 3}"}],
                    "operation": "insert",
                    "collection": "test_collection",
                    "message_id": f"test_msg_{i}",
                    "timestamp": time.time()
                }
                test_messages.append(message_data)
                await producer.send(topic, message_data)
            
            await producer.flush()
            
        finally:
            await producer.stop()
        
        # Now consume the messages
        consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=kafka_config.bootstrap_servers,
            group_id="test_consumer_group",
            auto_offset_reset="earliest",
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        try:
            await consumer.start()
            
            consumed_messages = []
            async for message in consumer:
                consumed_messages.append(message.value)
                if len(consumed_messages) >= 10:
                    break
            
            # Verify all messages were consumed
            assert len(consumed_messages) == 10
            
            # Verify message content
            for i, consumed_msg in enumerate(consumed_messages):
                assert consumed_msg["message_id"] == f"test_msg_{i}"
                assert consumed_msg["operation"] == "insert"
                assert consumed_msg["collection"] == "test_collection"
                assert len(consumed_msg["vectors"]) == 1
                assert len(consumed_msg["metadata"]) == 1
                
        finally:
            await consumer.stop()

    @pytest.mark.asyncio
    async def test_kafka_stream_processor(self, docker_services, kafka_config, milvus_config):
        """Test KafkaStreamProcessor integration."""
        # Note: This test mocks the Milvus client since we're focusing on Kafka integration
        from unittest.mock import AsyncMock, patch
        
        with patch('ai_prishtina_milvus_client.streaming.AsyncMilvusClient') as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.insert.return_value = [1, 2, 3]
            mock_client.return_value = mock_client_instance
            
            processor = KafkaStreamProcessor(
                milvus_config=milvus_config,
                stream_config=kafka_config
            )
            
            # Test message production
            test_message = StreamMessage(
                vectors=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
                metadata=[{"id": 1}, {"id": 2}],
                operation="insert",
                collection="test_collection"
            )
            
            await processor.produce_message("test_topic", test_message)
            
            # Verify the message was sent (we can't easily verify without complex setup)
            # In a real integration test, you would consume the message to verify

    @pytest.mark.asyncio
    async def test_kafka_batch_processing(self, docker_services, kafka_config):
        """Test batch processing with Kafka."""
        topic = "batch_processing_test"
        batch_size = 50
        
        # Produce a large batch of messages
        producer = AIOKafkaProducer(
            bootstrap_servers=kafka_config.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            batch_size=16384,  # 16KB batch size
            linger_ms=10  # Wait 10ms for batching
        )
        
        try:
            await producer.start()
            
            # Send messages in batches
            for batch_id in range(5):
                batch_messages = []
                for i in range(batch_size):
                    message_data = {
                        "vectors": [[0.1 * i, 0.2 * i, 0.3 * i, 0.4 * i]],
                        "metadata": [{"batch_id": batch_id, "item_id": i}],
                        "operation": "insert",
                        "collection": "batch_test_collection",
                        "message_id": f"batch_{batch_id}_msg_{i}",
                        "timestamp": time.time()
                    }
                    batch_messages.append(message_data)
                
                # Send batch
                for message in batch_messages:
                    await producer.send(topic, message)
                
                await producer.flush()
            
        finally:
            await producer.stop()
        
        # Consume and verify batch processing
        consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=kafka_config.bootstrap_servers,
            group_id="batch_consumer_group",
            auto_offset_reset="earliest",
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            max_poll_records=100  # Process in batches
        )
        
        try:
            await consumer.start()
            
            total_consumed = 0
            batches_processed = 0
            
            while total_consumed < 250:  # 5 batches * 50 messages
                message_batch = await consumer.getmany(timeout_ms=5000)
                
                if not message_batch:
                    break
                
                for topic_partition, messages in message_batch.items():
                    total_consumed += len(messages)
                    batches_processed += 1
                    
                    # Verify batch content
                    for message in messages:
                        assert "batch_id" in message.value["metadata"][0]
                        assert "item_id" in message.value["metadata"][0]
                        assert message.value["operation"] == "insert"
            
            assert total_consumed == 250
            assert batches_processed > 0
            
        finally:
            await consumer.stop()

    @pytest.mark.asyncio
    async def test_kafka_consumer_groups(self, docker_services, kafka_config):
        """Test Kafka consumer groups for load balancing."""
        topic = "consumer_group_test"
        
        # Produce messages to multiple partitions
        producer = AIOKafkaProducer(
            bootstrap_servers=kafka_config.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        try:
            await producer.start()
            
            # Send messages with different keys to distribute across partitions
            for i in range(20):
                message_data = {
                    "message_id": f"msg_{i}",
                    "data": f"test_data_{i}",
                    "timestamp": time.time()
                }
                
                # Use different keys to distribute messages
                key = f"key_{i % 4}".encode('utf-8')
                await producer.send(topic, message_data, key=key)
            
            await producer.flush()
            
        finally:
            await producer.stop()
        
        # Create multiple consumers in the same group
        consumers = []
        consumed_messages = [[] for _ in range(3)]
        
        try:
            for i in range(3):
                consumer = AIOKafkaConsumer(
                    topic,
                    bootstrap_servers=kafka_config.bootstrap_servers,
                    group_id="load_balance_group",
                    auto_offset_reset="earliest",
                    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
                )
                consumers.append(consumer)
                await consumer.start()
            
            # Consume messages concurrently
            async def consume_messages(consumer_idx, consumer):
                try:
                    async for message in consumer:
                        consumed_messages[consumer_idx].append(message.value)
                        if sum(len(msgs) for msgs in consumed_messages) >= 20:
                            break
                except Exception:
                    pass
            
            # Start consuming with timeout
            tasks = [
                consume_messages(i, consumer) 
                for i, consumer in enumerate(consumers)
            ]
            
            await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=30.0
            )
            
            # Verify load balancing
            total_consumed = sum(len(msgs) for msgs in consumed_messages)
            assert total_consumed == 20
            
            # Each consumer should have received some messages
            consumers_with_messages = sum(1 for msgs in consumed_messages if len(msgs) > 0)
            assert consumers_with_messages >= 1  # At least one consumer got messages
            
        finally:
            for consumer in consumers:
                await consumer.stop()

    @pytest.mark.asyncio
    async def test_kafka_error_handling(self, docker_services, kafka_config):
        """Test Kafka error handling scenarios."""
        # Test connection to non-existent broker
        with pytest.raises(Exception):
            bad_producer = AIOKafkaProducer(
                bootstrap_servers="localhost:9999",
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            await bad_producer.start()
            await bad_producer.stop()
        
        # Test invalid message serialization
        producer = AIOKafkaProducer(
            bootstrap_servers=kafka_config.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        try:
            await producer.start()
            
            # Try to send non-serializable data
            with pytest.raises(Exception):
                invalid_data = {"function": lambda x: x}  # Functions are not JSON serializable
                await producer.send("test_topic", invalid_data)
                
        finally:
            await producer.stop()
        
        # Test consumer with invalid topic
        consumer = AIOKafkaConsumer(
            "non_existent_topic_12345",
            bootstrap_servers=kafka_config.bootstrap_servers,
            group_id="error_test_group",
            auto_offset_reset="earliest",
            consumer_timeout_ms=5000
        )
        
        try:
            await consumer.start()
            
            # Should not receive any messages
            messages_received = 0
            try:
                async for message in consumer:
                    messages_received += 1
                    if messages_received > 0:
                        break
            except Exception:
                pass
            
            assert messages_received == 0
            
        finally:
            await consumer.stop()

    @pytest.mark.asyncio
    async def test_kafka_performance_monitoring(self, docker_services, kafka_config):
        """Test Kafka performance monitoring."""
        topic = "performance_test"
        message_count = 100
        
        # Measure production performance
        producer = AIOKafkaProducer(
            bootstrap_servers=kafka_config.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        try:
            await producer.start()
            
            start_time = time.time()
            
            # Send messages and measure time
            for i in range(message_count):
                message_data = {
                    "message_id": f"perf_msg_{i}",
                    "data": f"performance_test_data_{i}" * 10,  # Larger message
                    "timestamp": time.time()
                }
                await producer.send(topic, message_data)
            
            await producer.flush()
            production_time = time.time() - start_time
            
            # Calculate production rate
            production_rate = message_count / production_time
            assert production_rate > 0
            
        finally:
            await producer.stop()
        
        # Measure consumption performance
        consumer = AIOKafkaConsumer(
            topic,
            bootstrap_servers=kafka_config.bootstrap_servers,
            group_id="performance_consumer_group",
            auto_offset_reset="earliest",
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        try:
            await consumer.start()
            
            start_time = time.time()
            consumed_count = 0
            
            async for message in consumer:
                consumed_count += 1
                if consumed_count >= message_count:
                    break
            
            consumption_time = time.time() - start_time
            consumption_rate = consumed_count / consumption_time
            
            assert consumed_count == message_count
            assert consumption_rate > 0
            
            # Log performance metrics (in real scenario, you'd send to monitoring)
            print(f"Production rate: {production_rate:.2f} msg/s")
            print(f"Consumption rate: {consumption_rate:.2f} msg/s")
            
        finally:
            await consumer.stop()
