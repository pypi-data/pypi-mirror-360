"""
Focused security tests for actual security module.

Copyright (c) 2025 Alban Maxhuni <alban.q.maxhuni@gmail.com>

This software is dual-licensed under AGPL-3.0 (open-source) and Commercial licenses.
For commercial licensing, contact: alban.q.maxhuni@gmail.com
"""

import pytest
import asyncio
import base64
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from typing import List, Dict, Any

from ai_prishtina_milvus_client.security import (
    SecurityConfig,
    SecurityManager,
    User
)
from ai_prishtina_milvus_client.config import MilvusConfig
from ai_prishtina_milvus_client.exceptions import SecurityError


class TestSecurityFocused:
    """Focused security tests."""

    @pytest.fixture
    def security_config(self):
        """Create security configuration."""
        # Generate a proper Fernet key
        from cryptography.fernet import Fernet
        encryption_key = Fernet.generate_key().decode()

        return SecurityConfig(
            secret_key="test_secret_key_for_jwt_tokens",
            token_expiry=3600,
            encryption_key=encryption_key,
            allowed_ips=["127.0.0.1", "192.168.1.0/24"],
            require_ssl=True
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
    async def test_security_config_creation(self, security_config):
        """Test security configuration creation."""
        assert security_config.secret_key == "test_secret_key_for_jwt_tokens"
        assert security_config.token_expiry == 3600
        assert security_config.encryption_key is not None
        assert "127.0.0.1" in security_config.allowed_ips
        assert "192.168.1.0/24" in security_config.allowed_ips
        assert security_config.require_ssl is True

    @pytest.mark.asyncio
    async def test_security_manager_initialization(self, security_config):
        """Test security manager initialization."""
        manager = SecurityManager(config=security_config)

        # Verify initialization
        assert manager.config == security_config
        assert manager.users == {}
        assert manager.logger is not None

    @pytest.mark.asyncio
    async def test_user_creation(self, security_config):
        """Test user creation functionality."""
        manager = SecurityManager(config=security_config)

        # Test user creation
        await manager.create_user(
            username="test_user",
            password="test_password",
            roles=["read", "write"]
        )

        # Verify user was created
        assert "test_user" in manager.users
        user = manager.users["test_user"]
        assert user.username == "test_user"
        assert user.roles == ["read", "write"]
        assert user.password_hash is not None

    @pytest.mark.asyncio
    async def test_user_authentication(self, security_config):
        """Test user authentication."""
        manager = SecurityManager(config=security_config)

        # Create a user first
        await manager.create_user(
            username="auth_user",
            password="auth_password",
            roles=["read"]
        )

        # Test successful authentication
        token = await manager.authenticate("auth_user", "auth_password")
        assert token is not None
        assert isinstance(token, str)

        # Test failed authentication
        with pytest.raises(ValueError):
            await manager.authenticate("auth_user", "wrong_password")

    @pytest.mark.asyncio
    async def test_token_generation_and_validation(self, security_config):
        """Test token generation and validation."""
        manager = SecurityManager(config=security_config)

        # Create a user first
        await manager.create_user(
            username="token_user",
            password="token_password",
            roles=["read", "write"]
        )

        # Test token generation through authentication
        token = await manager.authenticate("token_user", "token_password")
        assert token is not None
        assert isinstance(token, str)

        # Test token validation
        user = await manager.verify_token(token)
        assert user.username == "token_user"
        assert user.roles == ["read", "write"]

    @pytest.mark.asyncio
    async def test_user_model(self):
        """Test User model functionality."""
        user = User(
            username="test_user",
            roles=["read", "write"],
            password_hash="hashed_password"
        )

        assert user.username == "test_user"
        assert user.roles == ["read", "write"]
        assert user.password_hash == "hashed_password"

    @pytest.mark.asyncio
    async def test_data_encryption(self, security_config):
        """Test data encryption functionality."""
        manager = SecurityManager(config=security_config)

        # Test data encryption
        original_data = "sensitive_information"
        encrypted_data = await manager.encrypt_data(original_data)

        # Verify encryption
        assert encrypted_data != original_data
        assert isinstance(encrypted_data, bytes)

        # Test data decryption
        decrypted_data = await manager.decrypt_data(encrypted_data)
        assert decrypted_data == original_data
