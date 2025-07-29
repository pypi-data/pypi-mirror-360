# Integration Tests

This directory contains comprehensive integration tests for the AI Prishtina Milvus Client that test against real services using Docker containers.

## Overview

The integration tests verify the functionality of the client against actual services rather than mocks, ensuring real-world compatibility and performance. These tests use Docker containers to provide consistent, isolated environments for testing.

## Supported Services

The integration tests cover the following services:

### Core Services
- **Milvus** - Vector database operations (insert, search, delete, collections, indexes)
- **Redis** - Caching, session management, pub/sub, streams, rate limiting
- **Kafka** - Message streaming, producer/consumer operations, batch processing
- **MinIO (S3)** - Cloud storage operations, backup/restore, large file handling

### Monitoring & Observability
- **Prometheus** - Metrics collection and querying
- **Pushgateway** - Metrics pushing for batch jobs
- **MailHog** - Email testing (SMTP simulation)

### Supporting Services
- **Etcd** - Distributed configuration (used by Milvus)
- **Zookeeper** - Coordination service (used by Kafka)

## Test Structure

```
tests/integration/
├── conftest.py                     # Test configuration and fixtures
├── test_milvus_integration.py      # Milvus vector database tests
├── test_redis_integration.py       # Redis caching and streaming tests
├── test_kafka_integration.py       # Kafka message streaming tests
├── test_cloud_storage_integration.py # MinIO/S3 storage tests
├── test_monitoring_integration.py  # Prometheus monitoring tests
├── test_end_to_end.py             # Complete workflow tests
└── README.md                      # This file
```

## Prerequisites

### Docker & Docker Compose
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Python Dependencies
```bash
pip install pytest pytest-asyncio pytest-cov
pip install docker redis boto3 requests
pip install aiokafka confluent-kafka
pip install prometheus-client
```

## Running Integration Tests

### Quick Start
```bash
# Run all integration tests
pytest tests/integration/ -v

# Run specific test file
pytest tests/integration/test_milvus_integration.py -v

# Run with coverage
pytest tests/integration/ --cov=ai_prishtina_milvus_client --cov-report=html
```

### Test Categories

#### By Service
```bash
# Milvus tests
pytest tests/integration/test_milvus_integration.py -v

# Redis tests  
pytest tests/integration/test_redis_integration.py -v

# Kafka tests
pytest tests/integration/test_kafka_integration.py -v

# Storage tests
pytest tests/integration/test_cloud_storage_integration.py -v

# Monitoring tests
pytest tests/integration/test_monitoring_integration.py -v

# End-to-end tests
pytest tests/integration/test_end_to_end.py -v
```

#### By Test Markers
```bash
# Run only integration tests
pytest -m integration

# Run only Docker-based tests
pytest -m docker

# Run slow tests (performance, load testing)
pytest -m slow

# Skip slow tests
pytest -m "not slow"
```

### Environment Variables

You can customize test behavior with environment variables:

```bash
# Service endpoints
export MILVUS_HOST=localhost
export MILVUS_PORT=19530
export REDIS_HOST=localhost
export REDIS_PORT=6379
export KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# Test configuration
export INTEGRATION_TEST_TIMEOUT=300
export INTEGRATION_TEST_CLEANUP=true
export INTEGRATION_TEST_VERBOSE=true
```

## Test Configuration

### Docker Services Configuration

The tests automatically start the required Docker services using the configuration in `conftest.py`. The services include:

- **Milvus**: Vector database with Etcd and MinIO dependencies
- **Redis**: In-memory data store
- **Kafka**: Message streaming with Zookeeper
- **MinIO**: S3-compatible object storage
- **Prometheus**: Metrics collection
- **Pushgateway**: Metrics pushing
- **MailHog**: Email testing

### Service Health Checks

All services include health checks to ensure they're ready before tests run:

- **Milvus**: HTTP health endpoint check
- **Redis**: PING command
- **Kafka**: Topic listing capability
- **MinIO**: Health endpoint check
- **Prometheus**: Ready endpoint check

### Timeouts and Retries

- **Service startup**: 120 seconds maximum wait
- **Individual tests**: 60 seconds default timeout
- **Health checks**: 5-second intervals with exponential backoff

## Test Categories

### 1. Milvus Integration Tests (`test_milvus_integration.py`)

- **Connection Management**: Connect, disconnect, health checks
- **Collection Lifecycle**: Create, list, describe, drop collections
- **Vector Operations**: Insert, search, delete vectors with metadata
- **Batch Operations**: Large-scale insert and search operations
- **Index Management**: Create, describe, drop indexes
- **Partition Operations**: Create, list, drop partitions
- **Error Handling**: Invalid operations, connection failures
- **Concurrent Operations**: Multi-threaded access patterns

### 2. Redis Integration Tests (`test_redis_integration.py`)

- **Basic Operations**: GET, SET, DELETE operations
- **Caching**: Vector caching, TTL management
- **Pub/Sub**: Message publishing and subscription
- **Streams**: Redis Streams for event processing
- **Session Management**: User session storage and retrieval
- **Rate Limiting**: Request rate limiting implementation
- **Distributed Locks**: Coordination between processes
- **Metrics Collection**: Performance metrics storage

### 3. Kafka Integration Tests (`test_kafka_integration.py`)

- **Producer/Consumer**: Message production and consumption
- **Stream Processing**: Vector data streaming
- **Batch Processing**: High-throughput batch operations
- **Consumer Groups**: Load balancing across consumers
- **Error Handling**: Connection failures, serialization errors
- **Performance**: Throughput and latency measurements

### 4. Cloud Storage Tests (`test_cloud_storage_integration.py`)

- **Basic Operations**: Upload, download, delete objects
- **Vector Storage**: Storing and retrieving vector data
- **Large Files**: Multipart upload for large datasets
- **Batch Operations**: Multiple file operations
- **Versioning**: Object versioning and lifecycle management
- **Error Handling**: Network failures, invalid operations
- **Performance**: Upload/download speed measurements

### 5. Monitoring Tests (`test_monitoring_integration.py`)

- **Prometheus Integration**: Metrics collection and querying
- **Custom Metrics**: Application-specific metrics
- **System Metrics**: CPU, memory, disk usage
- **Alerting**: Threshold-based alerting rules
- **Performance Monitoring**: Latency and throughput tracking
- **Dashboard Data**: Metrics export for visualization

### 6. End-to-End Tests (`test_end_to_end.py`)

- **Complete Pipeline**: Full vector processing workflow
- **High Availability**: Failover and recovery scenarios
- **Performance Under Load**: Stress testing with multiple services
- **Data Consistency**: Cross-service data integrity
- **Disaster Recovery**: Backup and restore procedures

## Performance Benchmarks

The integration tests include performance benchmarks:

### Milvus Performance
- **Insert Throughput**: > 1000 vectors/second
- **Search Latency**: < 100ms for top-10 search
- **Concurrent Operations**: 10+ simultaneous connections

### Redis Performance
- **Cache Operations**: < 1ms for GET/SET
- **Pub/Sub Latency**: < 10ms message delivery
- **Stream Processing**: > 10,000 messages/second

### Kafka Performance
- **Producer Throughput**: > 10,000 messages/second
- **Consumer Latency**: < 100ms end-to-end
- **Batch Processing**: 1MB+ batches efficiently

### Storage Performance
- **Upload Speed**: > 10MB/second
- **Download Speed**: > 20MB/second
- **Large Files**: 100MB+ files supported

## Troubleshooting

### Common Issues

#### Docker Services Not Starting
```bash
# Check Docker daemon
sudo systemctl status docker

# Check available ports
netstat -tulpn | grep -E "(19530|6379|9092|9000)"

# View service logs
docker-compose logs milvus
docker-compose logs redis
```

#### Test Timeouts
```bash
# Increase timeout for slow systems
export INTEGRATION_TEST_TIMEOUT=600

# Run with verbose output
pytest tests/integration/ -v -s
```

#### Memory Issues
```bash
# Increase Docker memory limit
# Edit Docker Desktop settings or /etc/docker/daemon.json

# Monitor resource usage
docker stats
```

### Debugging Tests

```bash
# Run single test with full output
pytest tests/integration/test_milvus_integration.py::TestMilvusIntegration::test_milvus_connection -v -s

# Enable debug logging
export PYTHONPATH=. 
export LOG_LEVEL=DEBUG
pytest tests/integration/ -v -s

# Keep containers running after test failure
export INTEGRATION_TEST_CLEANUP=false
pytest tests/integration/ -v
```

## Contributing

When adding new integration tests:

1. **Follow the existing patterns** in test structure and naming
2. **Add proper cleanup** in finally blocks or fixtures
3. **Include error handling tests** for failure scenarios
4. **Add performance assertions** where appropriate
5. **Update this README** with new test descriptions
6. **Use appropriate test markers** (`@pytest.mark.integration`, `@pytest.mark.slow`)

### Test Guidelines

- **Isolation**: Each test should be independent
- **Cleanup**: Always clean up resources (collections, files, etc.)
- **Assertions**: Include meaningful assertions with clear error messages
- **Documentation**: Add docstrings explaining test purpose
- **Performance**: Include reasonable performance expectations

## CI/CD Integration

For continuous integration, use:

```yaml
# .github/workflows/integration-tests.yml
name: Integration Tests
on: [push, pull_request]
jobs:
  integration:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-cov
      - name: Run integration tests
        run: pytest tests/integration/ -v --cov=ai_prishtina_milvus_client
```

## Security Considerations

- **Test Data**: Use only synthetic test data, never production data
- **Credentials**: Use test credentials, rotate regularly
- **Network**: Tests run in isolated Docker networks
- **Cleanup**: All test data is automatically cleaned up
- **Secrets**: No real secrets or API keys in test code
