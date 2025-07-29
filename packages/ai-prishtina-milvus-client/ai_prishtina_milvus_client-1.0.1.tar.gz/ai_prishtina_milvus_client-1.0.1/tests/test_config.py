"""
Tests for the configuration module.

Copyright (c) 2025 Alban Maxhuni <alban.q.maxhuni@gmail.com>

This software is dual-licensed under AGPL-3.0 (open-source) and Commercial licenses.
For commercial licensing, contact: alban.q.maxhuni@gmail.com
"""

import os
import tempfile
import pytest
import yaml
from pathlib import Path
from pydantic import ValidationError

from ai_prishtina_milvus_client.config import MilvusConfig


class TestMilvusConfig:
    """Test MilvusConfig class."""

    def test_config_creation(self):
        """Test basic config creation."""
        config = MilvusConfig(
            host="localhost",
            port=19530,
            collection_name="test_collection",
            dim=128
        )
        
        assert config.host == "localhost"
        assert config.port == 19530
        assert config.collection_name == "test_collection"
        assert config.dim == 128
        assert config.index_type == "IVF_FLAT"  # default
        assert config.metric_type == "L2"  # default

    def test_config_validation(self):
        """Test config validation."""
        # Test missing required fields
        with pytest.raises(ValidationError):
            MilvusConfig(host="localhost", port=19530)  # missing collection_name and dim
        
        # Test invalid port
        with pytest.raises(ValidationError):
            MilvusConfig(
                host="localhost",
                port=70000,  # invalid port
                collection_name="test",
                dim=128
            )
        
        # Test invalid dimension
        with pytest.raises(ValidationError):
            MilvusConfig(
                host="localhost",
                port=19530,
                collection_name="test",
                dim=0  # invalid dimension
            )

    def test_config_from_yaml(self):
        """Test loading config from YAML file."""
        config_data = {
            "milvus": {
                "host": "localhost",
                "port": 19530,
                "collection_name": "test_collection",
                "dim": 128,
                "index_type": "IVF_FLAT",
                "metric_type": "L2"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name
        
        try:
            config = MilvusConfig.from_yaml(config_path)
            assert config.host == "localhost"
            assert config.port == 19530
            assert config.collection_name == "test_collection"
            assert config.dim == 128
        finally:
            os.unlink(config_path)

    def test_config_to_yaml(self):
        """Test saving config to YAML file."""
        config = MilvusConfig(
            host="localhost",
            port=19530,
            collection_name="test_collection",
            dim=128
        )
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            config_path = f.name
        
        try:
            config.to_yaml(config_path)
            
            # Load and verify
            with open(config_path, 'r') as f:
                loaded_data = yaml.safe_load(f)
            
            assert loaded_data["milvus"]["host"] == "localhost"
            assert loaded_data["milvus"]["port"] == 19530
            assert loaded_data["milvus"]["collection_name"] == "test_collection"
            assert loaded_data["milvus"]["dim"] == 128
        finally:
            os.unlink(config_path)

    def test_config_file_not_found(self):
        """Test handling of missing config file."""
        with pytest.raises(FileNotFoundError):
            MilvusConfig.from_yaml("nonexistent_file.yaml")

    def test_invalid_yaml_file(self):
        """Test handling of invalid YAML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("invalid: yaml: content: [")
            config_path = f.name
        
        try:
            with pytest.raises(ValueError):
                MilvusConfig.from_yaml(config_path)
        finally:
            os.unlink(config_path)

    def test_config_with_metadata_fields(self):
        """Test config with metadata fields."""
        config = MilvusConfig(
            host="localhost",
            port=19530,
            collection_name="test_collection",
            dim=128,
            metadata_fields=[
                {"name": "text", "type": "string", "max_length": 1000},
                {"name": "score", "type": "float"}
            ]
        )

        assert len(config.metadata_fields) == 2
        assert config.metadata_fields[0]["name"] == "text"
        assert config.metadata_fields[1]["name"] == "score"

    def test_invalid_metadata_fields(self):
        """Test validation of metadata fields."""
        # Test missing name
        with pytest.raises(ValueError):
            MilvusConfig(
                host="localhost",
                port=19530,
                collection_name="test_collection",
                dim=128,
                metadata_fields=[{"type": "varchar"}]  # missing name
            )
        
        # Test missing type
        with pytest.raises(ValueError):
            MilvusConfig(
                host="localhost",
                port=19530,
                collection_name="test_collection",
                dim=128,
                metadata_fields=[{"name": "text"}]  # missing type
            )

    @pytest.mark.asyncio
    async def test_async_yaml_operations(self):
        """Test async YAML operations."""
        config = MilvusConfig(
            host="localhost",
            port=19530,
            collection_name="test_collection",
            dim=128
        )
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            config_path = f.name
        
        try:
            # Test async save
            await config.to_yaml_async(config_path)
            
            # Test async load
            loaded_config = await MilvusConfig.from_yaml_async(config_path)
            
            assert loaded_config.host == config.host
            assert loaded_config.port == config.port
            assert loaded_config.collection_name == config.collection_name
            assert loaded_config.dim == config.dim
        finally:
            os.unlink(config_path)

    def test_config_defaults(self):
        """Test default configuration values."""
        config = MilvusConfig(
            collection_name="test_collection",
            dim=128
        )
        
        assert config.host == "localhost"
        assert config.port == 19530
        assert config.db_name == "default"
        assert config.index_type == "IVF_FLAT"
        assert config.metric_type == "L2"
        assert config.nlist == 1024

    def test_config_string_validation(self):
        """Test string field validation."""
        # Test empty collection name
        with pytest.raises(ValidationError):
            MilvusConfig(
                collection_name="",  # empty string
                dim=128
            )
        
        # Test whitespace-only collection name
        with pytest.raises(ValidationError):
            MilvusConfig(
                collection_name="   ",  # whitespace only
                dim=128
            )

    def test_config_model_dump(self):
        """Test model serialization."""
        config = MilvusConfig(
            host="localhost",
            port=19530,
            collection_name="test_collection",
            dim=128
        )
        
        data = config.model_dump()
        
        assert isinstance(data, dict)
        assert data["host"] == "localhost"
        assert data["port"] == 19530
        assert data["collection_name"] == "test_collection"
        assert data["dim"] == 128
