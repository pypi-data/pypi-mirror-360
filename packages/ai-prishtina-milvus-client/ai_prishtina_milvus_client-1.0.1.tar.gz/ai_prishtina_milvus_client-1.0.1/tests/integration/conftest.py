"""
Integration test configuration and fixtures.

Copyright (c) 2025 Alban Maxhuni <alban.q.maxhuni@gmail.com>

This software is dual-licensed under AGPL-3.0 (open-source) and Commercial licenses.
For commercial licensing, contact: alban.q.maxhuni@gmail.com
"""

import pytest
import asyncio
import docker
import time
import redis
import os
import tempfile
import yaml
from typing import Dict, Any, Generator
from pathlib import Path

from ai_prishtina_milvus_client.config import MilvusConfig
from ai_prishtina_milvus_client.streaming import StreamConfig
from ai_prishtina_milvus_client.security import SecurityConfig


@pytest.fixture(scope="session")
def docker_client():
    """Docker client for managing containers."""
    return docker.from_env()


@pytest.fixture(scope="session")
def docker_compose_file():
    """Path to docker-compose file."""
    return Path(__file__).parent.parent.parent / "docker-compose.yml"


@pytest.fixture(scope="session")
def integration_docker_compose():
    """Extended docker-compose for integration tests."""
    compose_content = {
        "version": "3.8",
        "services": {
            "redis": {
                "image": "redis:7-alpine",
                "ports": ["6379:6379"],
                "command": "redis-server --appendonly yes",
                "healthcheck": {
                    "test": ["CMD", "redis-cli", "ping"],
                    "interval": "5s",
                    "timeout": "3s",
                    "retries": 5
                }
            },
            "kafka": {
                "image": "confluentinc/cp-kafka:latest",
                "ports": ["9092:9092"],
                "environment": {
                    "KAFKA_BROKER_ID": "1",
                    "KAFKA_ZOOKEEPER_CONNECT": "zookeeper:2181",
                    "KAFKA_ADVERTISED_LISTENERS": "PLAINTEXT://localhost:9092",
                    "KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR": "1",
                    "KAFKA_AUTO_CREATE_TOPICS_ENABLE": "true"
                },
                "depends_on": ["zookeeper"],
                "healthcheck": {
                    "test": ["CMD", "kafka-topics", "--bootstrap-server", "localhost:9092", "--list"],
                    "interval": "10s",
                    "timeout": "5s",
                    "retries": 5
                }
            },
            "zookeeper": {
                "image": "confluentinc/cp-zookeeper:latest",
                "ports": ["2181:2181"],
                "environment": {
                    "ZOOKEEPER_CLIENT_PORT": "2181",
                    "ZOOKEEPER_TICK_TIME": "2000"
                }
            },
            "minio": {
                "image": "minio/minio:latest",
                "ports": ["9000:9000", "9001:9001"],
                "environment": {
                    "MINIO_ROOT_USER": "minioadmin",
                    "MINIO_ROOT_PASSWORD": "minioadmin"
                },
                "command": "server /data --console-address ':9001'",
                "healthcheck": {
                    "test": ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"],
                    "interval": "30s",
                    "timeout": "20s",
                    "retries": 3
                }
            },
            "prometheus": {
                "image": "prom/prometheus:latest",
                "ports": ["9090:9090"],
                "command": [
                    "--config.file=/etc/prometheus/prometheus.yml",
                    "--storage.tsdb.path=/prometheus",
                    "--web.console.libraries=/etc/prometheus/console_libraries",
                    "--web.console.templates=/etc/prometheus/consoles",
                    "--web.enable-lifecycle"
                ]
            },
            "pushgateway": {
                "image": "prom/pushgateway:latest",
                "ports": ["9091:9091"]
            },
            "mailhog": {
                "image": "mailhog/mailhog:latest",
                "ports": ["1025:1025", "8025:8025"]
            },
            "etcd": {
                "image": "quay.io/coreos/etcd:v3.5.5",
                "ports": ["2379:2379"],
                "environment": {
                    "ETCD_AUTO_COMPACTION_MODE": "revision",
                    "ETCD_AUTO_COMPACTION_RETENTION": "1000",
                    "ETCD_QUOTA_BACKEND_BYTES": "4294967296",
                    "ETCD_SNAPSHOT_COUNT": "50000"
                },
                "command": "etcd -advertise-client-urls=http://127.0.0.1:2379 -listen-client-urls http://0.0.0.0:2379 --data-dir /etcd"
            },
            "milvus": {
                "image": "milvusdb/milvus:v2.3.3",
                "ports": ["19530:19530"],
                "environment": {
                    "ETCD_ENDPOINTS": "etcd:2379",
                    "MINIO_ADDRESS": "minio:9000"
                },
                "command": ["milvus", "run", "standalone"],
                "depends_on": ["etcd", "minio"],
                "healthcheck": {
                    "test": ["CMD", "curl", "-f", "http://localhost:9091/healthz"],
                    "interval": "30s",
                    "timeout": "20s",
                    "retries": 10
                }
            }
        }
    }
    
    # Create temporary docker-compose file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
        yaml.dump(compose_content, f)
        return f.name


@pytest.fixture(scope="session")
def docker_services(docker_client, integration_docker_compose):
    """Start and manage Docker services for integration tests."""
    import subprocess
    
    # Start services
    subprocess.run([
        "docker-compose", "-f", integration_docker_compose, "up", "-d"
    ], check=True)
    
    # Wait for services to be healthy
    max_wait = 120  # 2 minutes
    start_time = time.time()
    
    services_to_check = [
        ("redis", 6379),
        ("minio", 9000),
        ("prometheus", 9090),
        ("pushgateway", 9091),
        ("mailhog", 1025),
        ("milvus", 19530)
    ]
    
    for service_name, port in services_to_check:
        while time.time() - start_time < max_wait:
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                if result == 0:
                    break
            except Exception:
                pass
            time.sleep(2)
        else:
            raise RuntimeError(f"Service {service_name} failed to start within {max_wait} seconds")
    
    yield
    
    # Cleanup
    subprocess.run([
        "docker-compose", "-f", integration_docker_compose, "down", "-v"
    ], check=False)
    
    # Remove temporary file
    os.unlink(integration_docker_compose)


@pytest.fixture
def milvus_config():
    """Milvus configuration for integration tests."""
    return MilvusConfig(
        host="localhost",
        port=19530,
        collection_name="integration_test_collection",
        dim=128,
        index_type="IVF_FLAT",
        metric_type="L2",
        nlist=1024
    )


@pytest.fixture
def redis_client(docker_services):
    """Redis client for integration tests."""
    client = redis.Redis(host='localhost', port=6379, decode_responses=True)
    
    # Wait for Redis to be ready
    for _ in range(30):
        try:
            client.ping()
            break
        except redis.ConnectionError:
            time.sleep(1)
    else:
        raise RuntimeError("Redis not ready")
    
    yield client
    
    # Cleanup
    client.flushall()
    client.close()


@pytest.fixture
def kafka_config():
    """Kafka configuration for integration tests."""
    return StreamConfig(
        bootstrap_servers="localhost:9092",
        group_id="integration_test_group",
        topics=["integration_test_topic"],
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        max_poll_interval_ms=300000,
        session_timeout_ms=10000,
        max_poll_records=500,
        batch_size=100,
        num_workers=2
    )


@pytest.fixture
def minio_config():
    """MinIO configuration for integration tests."""
    return {
        "endpoint_url": "http://localhost:9000",
        "access_key": "minioadmin",
        "secret_key": "minioadmin",
        "bucket_name": "integration-test-bucket"
    }


@pytest.fixture
def security_config():
    """Security configuration for integration tests."""
    from cryptography.fernet import Fernet
    
    return SecurityConfig(
        secret_key="integration_test_secret_key_for_jwt_tokens_12345",
        token_expiry=3600,
        encryption_key=Fernet.generate_key().decode(),
        allowed_ips=["127.0.0.1", "localhost"],
        require_ssl=False  # Disabled for testing
    )


@pytest.fixture
def prometheus_config():
    """Prometheus configuration for integration tests."""
    return {
        "prometheus_url": "http://localhost:9090",
        "pushgateway_url": "http://localhost:9091"
    }


@pytest.fixture
def email_config():
    """Email configuration for integration tests (using MailHog)."""
    return {
        "smtp_host": "localhost",
        "smtp_port": 1025,
        "username": "test@example.com",
        "password": "test_password",
        "web_ui": "http://localhost:8025"
    }


@pytest.fixture
def sample_vectors():
    """Sample vectors for testing."""
    import numpy as np
    return np.random.rand(10, 128).tolist()


@pytest.fixture
def sample_metadata():
    """Sample metadata for testing."""
    return [
        {"id": i, "category": f"category_{i % 3}", "score": float(i * 0.1)}
        for i in range(10)
    ]


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Pytest markers for integration tests
pytest.mark.integration = pytest.mark.integration
pytest.mark.slow = pytest.mark.slow
pytest.mark.docker = pytest.mark.docker
