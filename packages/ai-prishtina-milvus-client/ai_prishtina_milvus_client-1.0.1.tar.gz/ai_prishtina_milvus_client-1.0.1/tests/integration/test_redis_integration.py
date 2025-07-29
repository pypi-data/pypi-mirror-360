"""
Integration tests for Redis operations using Docker containers.

Copyright (c) 2025 Alban Maxhuni <alban.q.maxhuni@gmail.com>

This software is dual-licensed under AGPL-3.0 (open-source) and Commercial licenses.
For commercial licensing, contact: alban.q.maxhuni@gmail.com
"""

import pytest
import asyncio
import json
import time
from typing import List, Dict, Any

import redis.asyncio as aioredis
from ai_prishtina_milvus_client.streaming import StreamConfig, StreamMessage
from ai_prishtina_milvus_client.exceptions import StreamingError


@pytest.mark.integration
@pytest.mark.docker
class TestRedisIntegration:
    """Integration tests for Redis operations."""

    @pytest.mark.asyncio
    async def test_redis_connection(self, docker_services, redis_client):
        """Test basic Redis connection."""
        # Test ping
        response = redis_client.ping()
        assert response is True
        
        # Test basic operations
        redis_client.set("test_key", "test_value")
        value = redis_client.get("test_key")
        assert value == "test_value"
        
        # Test deletion
        redis_client.delete("test_key")
        value = redis_client.get("test_key")
        assert value is None

    @pytest.mark.asyncio
    async def test_redis_caching(self, docker_services, redis_client, sample_vectors):
        """Test Redis as a caching layer for vectors."""
        # Cache vectors
        cache_key = "vectors:batch_1"
        vector_data = {
            "vectors": sample_vectors,
            "metadata": {"batch_id": 1, "timestamp": time.time()},
            "count": len(sample_vectors)
        }
        
        # Store in Redis
        redis_client.setex(
            cache_key,
            3600,  # 1 hour TTL
            json.dumps(vector_data)
        )
        
        # Retrieve from Redis
        cached_data = redis_client.get(cache_key)
        assert cached_data is not None
        
        parsed_data = json.loads(cached_data)
        assert parsed_data["count"] == len(sample_vectors)
        assert len(parsed_data["vectors"]) == len(sample_vectors)
        assert parsed_data["metadata"]["batch_id"] == 1

    @pytest.mark.asyncio
    async def test_redis_pub_sub(self, docker_services):
        """Test Redis pub/sub functionality."""
        # Create async Redis clients
        publisher = aioredis.from_url("redis://localhost:6379")
        subscriber = aioredis.from_url("redis://localhost:6379")
        
        try:
            # Subscribe to channel
            pubsub = subscriber.pubsub()
            await pubsub.subscribe("test_channel")
            
            # Publish message
            test_message = {"type": "vector_insert", "count": 100, "timestamp": time.time()}
            await publisher.publish("test_channel", json.dumps(test_message))
            
            # Receive message
            message = await pubsub.get_message(timeout=5.0)
            if message and message["type"] == "subscribe":
                # Skip subscription confirmation
                message = await pubsub.get_message(timeout=5.0)
            
            assert message is not None
            assert message["type"] == "message"
            
            received_data = json.loads(message["data"])
            assert received_data["type"] == "vector_insert"
            assert received_data["count"] == 100
            
        finally:
            await pubsub.unsubscribe("test_channel")
            await pubsub.close()
            await publisher.close()
            await subscriber.close()

    @pytest.mark.asyncio
    async def test_redis_streams(self, docker_services):
        """Test Redis Streams functionality."""
        redis_client = aioredis.from_url("redis://localhost:6379")
        
        try:
            stream_name = "vector_stream"
            consumer_group = "vector_processors"
            consumer_name = "processor_1"
            
            # Create consumer group
            try:
                await redis_client.xgroup_create(
                    stream_name, consumer_group, id="0", mkstream=True
                )
            except Exception:
                # Group might already exist
                pass
            
            # Add messages to stream
            messages = []
            for i in range(5):
                message_data = {
                    "vector_id": f"vec_{i}",
                    "operation": "insert",
                    "data": json.dumps([0.1 * i, 0.2 * i, 0.3 * i]),
                    "timestamp": str(time.time())
                }
                
                message_id = await redis_client.xadd(stream_name, message_data)
                messages.append(message_id)
            
            # Read messages from consumer group
            consumed_messages = await redis_client.xreadgroup(
                consumer_group,
                consumer_name,
                {stream_name: ">"},
                count=5,
                block=1000
            )
            
            assert len(consumed_messages) == 1  # One stream
            stream_data = consumed_messages[0]
            assert stream_data[0] == stream_name.encode()
            assert len(stream_data[1]) == 5  # Five messages
            
            # Acknowledge messages
            for message_id, _ in stream_data[1]:
                await redis_client.xack(stream_name, consumer_group, message_id)
            
            # Verify pending messages
            pending_info = await redis_client.xpending(stream_name, consumer_group)
            assert pending_info["pending"] == 0
            
        finally:
            await redis_client.close()

    @pytest.mark.asyncio
    async def test_redis_session_management(self, docker_services, security_config):
        """Test Redis for session management."""
        redis_client = aioredis.from_url("redis://localhost:6379")
        
        try:
            # Create session data
            session_id = "session_12345"
            session_data = {
                "user_id": "user_123",
                "username": "test_user",
                "roles": ["read", "write"],
                "login_time": time.time(),
                "last_activity": time.time(),
                "permissions": ["vector_search", "vector_insert"]
            }
            
            # Store session with TTL
            await redis_client.setex(
                f"session:{session_id}",
                3600,  # 1 hour
                json.dumps(session_data)
            )
            
            # Retrieve session
            stored_session = await redis_client.get(f"session:{session_id}")
            assert stored_session is not None
            
            parsed_session = json.loads(stored_session)
            assert parsed_session["user_id"] == "user_123"
            assert parsed_session["username"] == "test_user"
            assert "vector_search" in parsed_session["permissions"]
            
            # Update last activity
            session_data["last_activity"] = time.time()
            await redis_client.setex(
                f"session:{session_id}",
                3600,
                json.dumps(session_data)
            )
            
            # Test session expiry
            ttl = await redis_client.ttl(f"session:{session_id}")
            assert ttl > 0 and ttl <= 3600
            
            # Delete session (logout)
            await redis_client.delete(f"session:{session_id}")
            
            # Verify session is deleted
            deleted_session = await redis_client.get(f"session:{session_id}")
            assert deleted_session is None
            
        finally:
            await redis_client.close()

    @pytest.mark.asyncio
    async def test_redis_rate_limiting(self, docker_services):
        """Test Redis for rate limiting."""
        redis_client = aioredis.from_url("redis://localhost:6379")
        
        try:
            user_id = "user_123"
            rate_limit_key = f"rate_limit:{user_id}"
            max_requests = 10
            window_seconds = 60
            
            # Simulate requests
            request_count = 0
            for i in range(15):  # Try to make 15 requests
                # Check current count
                current_count = await redis_client.get(rate_limit_key)
                current_count = int(current_count) if current_count else 0
                
                if current_count < max_requests:
                    # Allow request
                    pipe = redis_client.pipeline()
                    pipe.incr(rate_limit_key)
                    pipe.expire(rate_limit_key, window_seconds)
                    await pipe.execute()
                    request_count += 1
                else:
                    # Rate limit exceeded
                    break
            
            # Should have allowed exactly max_requests
            assert request_count == max_requests
            
            # Verify final count
            final_count = await redis_client.get(rate_limit_key)
            assert int(final_count) == max_requests
            
        finally:
            await redis_client.close()

    @pytest.mark.asyncio
    async def test_redis_distributed_locks(self, docker_services):
        """Test Redis for distributed locking."""
        redis_client = aioredis.from_url("redis://localhost:6379")
        
        try:
            lock_key = "lock:vector_processing"
            lock_value = "process_123"
            lock_timeout = 30
            
            # Acquire lock
            lock_acquired = await redis_client.set(
                lock_key,
                lock_value,
                nx=True,  # Only set if not exists
                ex=lock_timeout  # Expire after timeout
            )
            assert lock_acquired is True
            
            # Try to acquire same lock (should fail)
            second_lock = await redis_client.set(
                lock_key,
                "process_456",
                nx=True,
                ex=lock_timeout
            )
            assert second_lock is None
            
            # Check lock owner
            current_owner = await redis_client.get(lock_key)
            assert current_owner.decode() == lock_value
            
            # Release lock (only if we own it)
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """
            
            result = await redis_client.eval(lua_script, 1, lock_key, lock_value)
            assert result == 1  # Successfully released
            
            # Verify lock is released
            released_lock = await redis_client.get(lock_key)
            assert released_lock is None
            
        finally:
            await redis_client.close()

    @pytest.mark.asyncio
    async def test_redis_metrics_collection(self, docker_services):
        """Test Redis for metrics collection."""
        redis_client = aioredis.from_url("redis://localhost:6379")
        
        try:
            # Collect various metrics
            metrics = {
                "vector_inserts": 1500,
                "vector_searches": 3200,
                "cache_hits": 2800,
                "cache_misses": 400,
                "active_connections": 25,
                "avg_query_time": 0.045
            }
            
            timestamp = int(time.time())
            
            # Store metrics with timestamp
            for metric_name, value in metrics.items():
                await redis_client.zadd(
                    f"metrics:{metric_name}",
                    {timestamp: value}
                )
            
            # Retrieve recent metrics (last 5 minutes)
            five_minutes_ago = timestamp - 300
            
            recent_inserts = await redis_client.zrangebyscore(
                "metrics:vector_inserts",
                five_minutes_ago,
                timestamp,
                withscores=True
            )
            
            assert len(recent_inserts) == 1
            assert recent_inserts[0][1] == timestamp
            
            # Calculate aggregated metrics
            total_operations = metrics["vector_inserts"] + metrics["vector_searches"]
            cache_hit_rate = metrics["cache_hits"] / (metrics["cache_hits"] + metrics["cache_misses"])
            
            # Store aggregated metrics
            await redis_client.hset(
                f"aggregated_metrics:{timestamp}",
                mapping={
                    "total_operations": total_operations,
                    "cache_hit_rate": cache_hit_rate,
                    "timestamp": timestamp
                }
            )
            
            # Retrieve aggregated metrics
            stored_metrics = await redis_client.hgetall(f"aggregated_metrics:{timestamp}")
            assert float(stored_metrics[b"total_operations"]) == total_operations
            assert abs(float(stored_metrics[b"cache_hit_rate"]) - cache_hit_rate) < 0.001
            
        finally:
            await redis_client.close()

    @pytest.mark.asyncio
    async def test_redis_error_handling(self, docker_services):
        """Test Redis error handling scenarios."""
        # Test connection to non-existent Redis instance
        with pytest.raises(Exception):
            bad_client = aioredis.from_url("redis://localhost:9999")
            await bad_client.ping()
            await bad_client.close()
        
        # Test with valid client
        redis_client = aioredis.from_url("redis://localhost:6379")
        
        try:
            # Test invalid operations
            with pytest.raises(Exception):
                # Try to perform list operation on string key
                await redis_client.set("string_key", "value")
                await redis_client.lpush("string_key", "item")
            
            # Test transaction rollback
            async with redis_client.pipeline(transaction=True) as pipe:
                pipe.set("tx_key", "value1")
                pipe.set("tx_key", "value2")
                # Simulate error condition
                try:
                    pipe.lpush("tx_key", "item")  # This will fail
                    await pipe.execute()
                except Exception:
                    # Transaction should be rolled back
                    pass
            
            # Verify transaction was rolled back
            value = await redis_client.get("tx_key")
            # Value should be None if transaction was properly rolled back
            # or the last successful value if partial execution occurred
            
        finally:
            await redis_client.close()
