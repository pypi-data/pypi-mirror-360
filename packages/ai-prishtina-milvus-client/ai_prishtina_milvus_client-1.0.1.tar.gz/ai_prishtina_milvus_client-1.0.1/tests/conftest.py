"""
Pytest configuration and fixtures.

Copyright (c) 2025 Alban Maxhuni <alban.q.maxhuni@gmail.com>

This software is dual-licensed under AGPL-3.0 (open-source) and Commercial licenses.
For commercial licensing, contact: alban.q.maxhuni@gmail.com
"""

import pytest
import pytest_asyncio
import numpy as np
import tempfile
import yaml
from typing import List, Dict, Any
from unittest.mock import MagicMock, patch
from ai_prishtina_milvus_client import (
    MilvusClient,
    MilvusConfig,
    DataValidator,
    VectorValidationConfig,
    BatchConfig,
    MonitoringConfig,
    RetryConfig,
    DataManagementConfig,
    SecurityConfig,
    SearchConfig,
    DataValidationConfig,
    DataCleaningConfig,
    DataTransformationConfig,
    PerformanceConfig,
    LoggingConfig,
    DebugConfig,
    TestConfig
)
from ai_prishtina_milvus_client.client import AsyncMilvusClient

@pytest.fixture
def milvus_config() -> MilvusConfig:
    """Create Milvus configuration for testing."""
    return MilvusConfig(
        host="localhost",
        port=19530,
        collection_name="test_collection",
        dim=128,
        index_type="IVF_FLAT",
        metric_type="L2",
        nlist=1024,
    )

@pytest.fixture
def config_file(milvus_config):
    """Create a temporary config file for testing."""
    config_data = {"milvus": milvus_config.model_dump()}

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(config_data, f)
        return f.name

@pytest.fixture
def sample_vectors() -> List[List[float]]:
    """Generate sample vectors for testing."""
    return np.random.rand(10, 128).tolist()

@pytest.fixture
def sample_metadata() -> List[Dict[str, Any]]:
    """Generate sample metadata for testing."""
    return [
        {
            "id": i,
            "text": f"Sample text {i}",
            "category": f"Category {i % 3}",
            "score": float(i) / 10.0
        }
        for i in range(10)
    ]

@pytest.fixture
def vector_validation_config() -> VectorValidationConfig:
    """Create vector validation configuration."""
    return VectorValidationConfig(
        expected_dim=128,
        normalize=True,
        check_type=True
    )

@pytest.fixture
def batch_config() -> BatchConfig:
    """Create batch configuration."""
    return BatchConfig(
        batch_size=1000,
        max_workers=4,
        show_progress=True
    )

@pytest.fixture
def monitoring_config() -> MonitoringConfig:
    """Create monitoring configuration."""
    return MonitoringConfig(
        collect_system_metrics=True,
        metrics_history_size=1000,
        collection_interval=1.0
    )

@pytest.fixture
def retry_config() -> RetryConfig:
    """Create retry configuration."""
    return RetryConfig(
        max_attempts=3,
        backoff_factor=2.0
    )

@pytest.fixture
def backup_config() -> DataManagementConfig:
    """Create backup configuration."""
    return DataManagementConfig(
        backup_dir="backups",
        export_dir="exports",
        import_dir="imports",
        max_backups=5
    )

@pytest.fixture
def security_config() -> SecurityConfig:
    """Create security configuration."""
    return SecurityConfig(
        secret_key="test_secret_key",
        token_expiry=3600,
        require_ssl=True
    )

@pytest.fixture
def search_config() -> SearchConfig:
    """Create search configuration."""
    return SearchConfig(
        metric_type="L2",
        top_k=10,
        nprobe=10
    )

@pytest.fixture
def data_validation_config() -> DataValidationConfig:
    """Create data validation configuration."""
    return DataValidationConfig(
        required_fields=["id", "text"],
        field_types={"id": "int", "score": "float"}
    )

@pytest.fixture
def data_cleaning_config() -> DataCleaningConfig:
    """Create data cleaning configuration."""
    return DataCleaningConfig(
        remove_duplicates=True,
        fill_missing=True,
        normalize=True
    )

@pytest.fixture
def data_transformation_config() -> DataTransformationConfig:
    """Create data transformation configuration."""
    return DataTransformationConfig(
        vector_normalization=True,
        field_mappings={"old_field": "new_field"}
    )

@pytest.fixture
def performance_config() -> PerformanceConfig:
    """Create performance configuration."""
    return PerformanceConfig(
        use_threading=True,
        use_multiprocessing=False
    )

@pytest.fixture
def logging_config() -> LoggingConfig:
    """Create logging configuration."""
    return LoggingConfig(
        level="INFO",
        file="test.log"
    )

@pytest.fixture
def debug_config() -> DebugConfig:
    """Create debug configuration."""
    return DebugConfig(
        enabled=True,
        break_on_error=False,
        trace_calls=True
    )

@pytest.fixture
def test_config() -> TestConfig:
    """Create test configuration."""
    return TestConfig(
        test_dir="tests",
        pattern="test_*.py",
        coverage=True
    )

@pytest.fixture
def mock_milvus():
    """Mock Milvus connections and operations."""
    with patch('ai_prishtina_milvus_client.client.connections') as mock_conn, \
         patch('ai_prishtina_milvus_client.client.Collection') as mock_collection, \
         patch('ai_prishtina_milvus_client.client.utility') as mock_utility:

        # Mock connection
        mock_conn.connect.return_value = None
        mock_conn.disconnect.return_value = None

        # Mock collection
        mock_coll_instance = MagicMock()
        mock_collection.return_value = mock_coll_instance
        mock_coll_instance.insert.return_value = MagicMock(primary_keys=[1, 2, 3])
        mock_coll_instance.search.return_value = [[{"id": 1, "distance": 0.1}]]
        mock_coll_instance.query.return_value = [{"id": 1, "vector": [0.1, 0.2]}]
        mock_coll_instance.delete.return_value = MagicMock(delete_count=3)

        # Mock utility
        mock_utility.has_collection.return_value = True
        mock_utility.list_collections.return_value = ["test_collection"]
        mock_utility.drop_collection.return_value = None

        yield {
            'connections': mock_conn,
            'collection': mock_collection,
            'utility': mock_utility
        }

@pytest.fixture
def client(milvus_config, mock_milvus):
    """Create a mocked Milvus client for testing."""
    return MilvusClient(milvus_config)

@pytest_asyncio.fixture
async def milvus_client(milvus_config, mock_milvus):
    """Create async Milvus client for testing."""
    with patch('ai_prishtina_milvus_client.client.AsyncMilvusClient._connect') as mock_connect, \
         patch('ai_prishtina_milvus_client.client.AsyncMilvusClient.close') as mock_close:

        mock_connect.return_value = None
        mock_close.return_value = None

        client = AsyncMilvusClient(milvus_config)
        # Mock the collection
        if 'collection' in mock_milvus:
            client._collection = mock_milvus['collection'].return_value
        yield client
        # No cleanup needed for mocked client

@pytest.fixture
def test_collection_data():
    """Generate test collection data."""
    return {
        "vectors": np.random.rand(10, 128).tolist(),
        "metadata": [{"id": i, "text": f"text_{i}"} for i in range(10)]
    }

@pytest.fixture
def test_collection():
    """Test collection name."""
    return "test_collection"

@pytest.fixture
def sample_data():
    """Generate sample data for testing."""
    return [
        {
            "id": i,
            "text": f"Sample text {i}",
            "category": f"Category {i % 3}",
            "score": float(i) / 10.0,
            "vector": np.random.rand(128).tolist()
        }
        for i in range(10)
    ]