"""
Configuration management for the Milvus client with async support.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any

import yaml
import aiofiles

# Handle Pydantic v1/v2 compatibility
try:
    from pydantic import BaseModel, Field, ConfigDict
    PYDANTIC_V2 = True
except ImportError:
    from pydantic import BaseModel, Field
    PYDANTIC_V2 = False
    # For v1 compatibility
    ConfigDict = None


class MilvusConfig(BaseModel):
    """Configuration model for Milvus connection and collection settings."""

    # Pydantic v2 configuration
    if PYDANTIC_V2:
        model_config = ConfigDict(
            validate_assignment=True,
            extra="forbid",
            str_strip_whitespace=True
        )
    else:
        # Pydantic v1 configuration
        class Config:
            validate_assignment = True
            extra = "forbid"
            anystr_strip_whitespace = True

    host: str = Field(default="localhost", description="Milvus server host")
    port: int = Field(default=19530, description="Milvus server port", ge=1, le=65535)
    user: Optional[str] = Field(default=None, description="Milvus username")
    password: Optional[str] = Field(default=None, description="Milvus password")
    db_name: str = Field(default="default", description="Database name")
    collection_name: str = Field(..., description="Collection name", min_length=1)
    dim: int = Field(..., description="Vector dimension", ge=1)
    index_type: str = Field(default="IVF_FLAT", description="Index type")
    metric_type: str = Field(default="L2", description="Distance metric type")
    nlist: int = Field(default=1024, description="Number of clusters for IVF index", ge=1)
    metadata_fields: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="List of metadata fields for the collection schema. Each field should be a dict with 'name' and 'type'."
    )
    
    @classmethod
    def from_yaml(cls, config_path: str) -> "MilvusConfig":
        """
        Load configuration from a YAML file synchronously.

        Args:
            config_path: Path to the YAML configuration file

        Returns:
            MilvusConfig instance

        Raises:
            FileNotFoundError: If the config file doesn't exist
            yaml.YAMLError: If the YAML file is invalid
            ValueError: If the configuration is invalid
        """
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML file: {e}")

        if not isinstance(config_data, dict):
            raise ValueError("Configuration file must contain a valid YAML dictionary")

        if "milvus" not in config_data:
            raise ValueError("Configuration file must contain a 'milvus' section")

        try:
            return cls(**config_data["milvus"])
        except Exception as e:
            raise ValueError(f"Invalid configuration: {e}")

    @classmethod
    async def from_yaml_async(cls, config_path: str) -> "MilvusConfig":
        """
        Load configuration from a YAML file asynchronously.

        Args:
            config_path: Path to the YAML configuration file

        Returns:
            MilvusConfig instance

        Raises:
            FileNotFoundError: If the config file doesn't exist
            yaml.YAMLError: If the YAML file is invalid
            ValueError: If the configuration is invalid
        """
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        try:
            async with aiofiles.open(config_path, encoding='utf-8') as f:
                content = await f.read()
                config_data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML file: {e}")

        if not isinstance(config_data, dict):
            raise ValueError("Configuration file must contain a valid YAML dictionary")

        if "milvus" not in config_data:
            raise ValueError("Configuration file must contain a 'milvus' section")

        try:
            return cls(**config_data["milvus"])
        except Exception as e:
            raise ValueError(f"Invalid configuration: {e}")
    
    def to_yaml(self, config_path: str) -> None:
        """
        Save configuration to a YAML file synchronously.

        Args:
            config_path: Path to save the YAML configuration file

        Raises:
            IOError: If writing to file fails
        """
        config_path = Path(config_path)
        config_data = {"milvus": self.model_dump()}

        try:
            # Ensure parent directory exists
            config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(config_path, "w", encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, indent=2)
        except Exception as e:
            raise IOError(f"Failed to write configuration file: {e}")

    async def to_yaml_async(self, config_path: str) -> None:
        """
        Save configuration to a YAML file asynchronously.

        Args:
            config_path: Path to save the YAML configuration file

        Raises:
            IOError: If writing to file fails
        """
        config_path = Path(config_path)
        config_data = {"milvus": self.model_dump()}

        try:
            # Ensure parent directory exists
            config_path.parent.mkdir(parents=True, exist_ok=True)

            async with aiofiles.open(config_path, "w", encoding='utf-8') as f:
                await f.write(yaml.dump(config_data, default_flow_style=False, indent=2))
        except Exception as e:
            raise IOError(f"Failed to write configuration file: {e}")

    def validate_metadata_fields(self) -> None:
        """
        Validate metadata fields configuration.

        Raises:
            ValueError: If metadata fields configuration is invalid
        """
        if self.metadata_fields is None:
            return

        if not isinstance(self.metadata_fields, list):
            raise ValueError("metadata_fields must be a list")

        valid_types = {"int", "int64", "float", "float32", "double", "float64",
                      "str", "string", "bool", "json"}

        for i, field in enumerate(self.metadata_fields):
            if not isinstance(field, dict):
                raise ValueError(f"metadata_fields[{i}] must be a dictionary")

            if "name" not in field:
                raise ValueError(f"metadata_fields[{i}] must have a 'name' key")

            if "type" not in field:
                raise ValueError(f"metadata_fields[{i}] must have a 'type' key")

            if not isinstance(field["name"], str) or not field["name"].strip():
                raise ValueError(f"metadata_fields[{i}]['name'] must be a non-empty string")

            if field["type"].lower() not in valid_types:
                raise ValueError(f"metadata_fields[{i}]['type'] must be one of {valid_types}")

    def model_post_init(self, __context: Any) -> None:
        """Post-initialization validation."""
        self.validate_metadata_fields()