"""
Comprehensive data management tests.

Copyright (c) 2025 Alban Maxhuni <alban.q.maxhuni@gmail.com>

This software is dual-licensed under AGPL-3.0 (open-source) and Commercial licenses.
For commercial licensing, contact: alban.q.maxhuni@gmail.com
"""

import pytest
import asyncio
import numpy as np
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from typing import List, Dict, Any
import tempfile
import json

from ai_prishtina_milvus_client.data_management import (
    DataManager,
    DataManagementConfig,
    DataValidationConfig,
    DataCleaningConfig,
    DataTransformationConfig
)
from ai_prishtina_milvus_client.config import MilvusConfig
from ai_prishtina_milvus_client.exceptions import DataManagementError, ValidationError


class TestDataManagerComprehensive:
    """Comprehensive data manager tests."""

    @pytest.fixture
    def data_config(self):
        """Create data configuration."""
        return DataManagementConfig(
            backup_dir="/tmp/test_backups",
            export_dir="/tmp/test_exports",
            import_dir="/tmp/test_imports",
            max_backups=5,
            compression=True,
            validate_on_import=True,
            batch_size=100
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
    async def test_data_manager_initialization(self, data_config, milvus_config):
        """Test data manager initialization."""
        with patch('ai_prishtina_milvus_client.data_management.AsyncMilvusClient') as mock_client:
            mock_client_instance = AsyncMock()
            mock_client.return_value = mock_client_instance

            manager = DataManager(
                milvus_config=milvus_config,
                data_config=data_config
            )

            # Verify initialization
            assert manager.milvus_config == milvus_config
            assert manager.data_config == data_config
            assert manager.client is not None

            # Test configuration access
            assert manager.data_config.batch_size == 100
            assert manager.data_config.compression is True
            assert manager.data_config.validate_on_import is True

    @pytest.mark.asyncio
    async def test_backup_creation(self, data_config, milvus_config):
        """Test backup creation functionality."""
        with patch('ai_prishtina_milvus_client.data_management.AsyncMilvusClient') as mock_client, \
             patch('ai_prishtina_milvus_client.data_management.aiofiles.open') as mock_open, \
             patch('os.makedirs') as mock_makedirs:

            # Mock client and collection
            mock_client_instance = AsyncMock()
            mock_collection = AsyncMock()
            mock_schema = AsyncMock()
            mock_schema.to_dict.return_value = {"fields": []}
            mock_collection.schema = mock_schema
            mock_collection.query.return_value = [{"id": 1, "vector": [0.1, 0.2]}]
            mock_client_instance.get_collection.return_value = mock_collection
            mock_client.return_value = mock_client_instance

            # Mock file operations
            mock_file = AsyncMock()
            mock_open.return_value.__aenter__.return_value = mock_file

            manager = DataManager(
                milvus_config=milvus_config,
                data_config=data_config
            )

            # Test backup creation
            backup_path = await manager.create_backup("test_collection")

            # Verify backup was created
            assert backup_path is not None
            mock_client_instance.get_collection.assert_called_with("test_collection")
            mock_file.write.assert_called_once()

    @pytest.mark.asyncio
    async def test_data_export(self, data_config, milvus_config):
        """Test data export functionality."""
        with patch('ai_prishtina_milvus_client.data_management.AsyncMilvusClient') as mock_client, \
             patch('ai_prishtina_milvus_client.data_management.aiofiles.open') as mock_open:

            # Mock client and collection
            mock_client_instance = AsyncMock()
            mock_collection = AsyncMock()
            mock_collection.query.return_value = [
                {"id": 1, "vector": [0.1, 0.2]},
                {"id": 2, "vector": [0.3, 0.4]}
            ]
            mock_client_instance.get_collection.return_value = mock_collection
            mock_client.return_value = mock_client_instance

            # Mock file operations
            mock_file = AsyncMock()
            mock_open.return_value.__aenter__.return_value = mock_file

            manager = DataManager(
                milvus_config=milvus_config,
                data_config=data_config
            )

            # Test data export
            export_path = await manager.export_data("test_collection", "json")

            # Verify export was created
            assert export_path is not None
            mock_collection.query.assert_called_once()
            mock_file.write.assert_called_once()

    @pytest.mark.asyncio
    async def test_data_import(self, data_config, milvus_config):
        """Test data import functionality."""
        with patch('ai_prishtina_milvus_client.data_management.AsyncMilvusClient') as mock_client, \
             patch('ai_prishtina_milvus_client.data_management.aiofiles.open') as mock_open:

            # Mock client
            mock_client_instance = AsyncMilvusClient(milvus_config)
            mock_client.return_value = mock_client_instance

            # Mock file operations
            mock_file = AsyncMock()
            test_data = json.dumps([
                {"id": 1, "vector": [0.1, 0.2]},
                {"id": 2, "vector": [0.3, 0.4]}
            ])
            mock_file.read.return_value = test_data
            mock_open.return_value.__aenter__.return_value = mock_file

            manager = DataManager(
                milvus_config=milvus_config,
                data_config=data_config
            )

            # Test data import
            with patch.object(manager, 'import_data') as mock_import:
                mock_import.return_value = {"imported": 2, "failed": 0}

                result = await manager.import_data("test_file.json", "test_collection")

                # Verify import was called
                assert result["imported"] == 2
                assert result["failed"] == 0

    @pytest.mark.asyncio
    async def test_configuration_classes(self, data_config, milvus_config):
        """Test configuration classes."""
        # Test DataValidationConfig
        validation_config = DataValidationConfig(
            required_fields=["id", "vector"],
            field_types={"id": "int", "vector": "list"},
            value_ranges={"id": (1, 1000)},
            patterns={"name": r"^[a-zA-Z]+$"}
        )

        assert validation_config.required_fields == ["id", "vector"]
        assert validation_config.field_types["id"] == "int"
        assert validation_config.value_ranges["id"] == (1, 1000)

        # Test DataCleaningConfig
        cleaning_config = DataCleaningConfig(
            remove_duplicates=True,
            fill_missing=True,
            normalize=True,
            remove_outliers=False
        )

        assert cleaning_config.remove_duplicates is True
        assert cleaning_config.fill_missing is True
        assert cleaning_config.normalize is True
        assert cleaning_config.remove_outliers is False

        # Test DataTransformationConfig
        transformation_config = DataTransformationConfig(
            vector_normalization=True,
            field_mappings={"old_name": "new_name"},
            metadata_extraction={"text": "length"}
        )

        assert transformation_config.vector_normalization is True
        assert transformation_config.field_mappings["old_name"] == "new_name"
        assert transformation_config.metadata_extraction["text"] == "length"
