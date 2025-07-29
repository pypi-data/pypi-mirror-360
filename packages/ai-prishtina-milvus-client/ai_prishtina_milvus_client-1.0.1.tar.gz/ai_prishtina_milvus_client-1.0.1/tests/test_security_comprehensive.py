"""
Comprehensive security tests.

Copyright (c) 2025 Alban Maxhuni <alban.q.maxhuni@gmail.com>

This software is dual-licensed under AGPL-3.0 (open-source) and Commercial licenses.
For commercial licensing, contact: alban.q.maxhuni@gmail.com
"""

import pytest
import asyncio
import base64
import json
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from typing import List, Dict, Any

from ai_prishtina_milvus_client.security import (
    SecurityConfig,
    SecurityManager,
    EncryptionManager,
    AuthenticationManager,
    AccessControlManager,
    AuditLogger
)
from ai_prishtina_milvus_client.config import MilvusConfig
from ai_prishtina_milvus_client.exceptions import SecurityError


class TestSecurityManagerComprehensive:
    """Comprehensive security manager tests."""

    @pytest.fixture
    def security_config(self):
        """Create security configuration."""
        return SecurityConfig(
            enable_encryption=True,
            encryption_key="test_encryption_key_32_bytes_long",
            enable_authentication=True,
            auth_method="token",
            enable_access_control=True,
            enable_audit_logging=True,
            audit_log_file="/tmp/audit.log",
            token_expiry_hours=24,
            max_login_attempts=3
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
    async def test_security_manager_initialization(self, security_config, milvus_config):
        """Test security manager initialization."""
        manager = SecurityManager(
            security_config=security_config,
            milvus_config=milvus_config
        )
        
        await manager.initialize()
        
        # Verify components are initialized
        assert manager.encryption_manager is not None
        assert manager.auth_manager is not None
        assert manager.access_control_manager is not None
        assert manager.audit_logger is not None
        
        # Test security status
        status = await manager.get_security_status()
        assert status["encryption_enabled"] is True
        assert status["authentication_enabled"] is True
        assert status["access_control_enabled"] is True
        assert status["audit_logging_enabled"] is True

    @pytest.mark.asyncio
    async def test_encryption_manager(self, security_config, milvus_config):
        """Test encryption manager functionality."""
        with patch('ai_prishtina_milvus_client.security.Fernet') as mock_fernet:
            
            # Mock Fernet encryption
            mock_fernet_instance = MagicMock()
            mock_fernet_instance.encrypt.return_value = b"encrypted_data"
            mock_fernet_instance.decrypt.return_value = b"original_data"
            mock_fernet.return_value = mock_fernet_instance
            
            encryption_manager = EncryptionManager(security_config)
            await encryption_manager.initialize()
            
            # Test data encryption
            original_data = "sensitive_data"
            encrypted_data = await encryption_manager.encrypt_data(original_data)
            
            # Verify encryption was called
            mock_fernet_instance.encrypt.assert_called()
            
            # Test data decryption
            decrypted_data = await encryption_manager.decrypt_data(encrypted_data)
            
            # Verify decryption was called
            mock_fernet_instance.decrypt.assert_called()

    @pytest.mark.asyncio
    async def test_vector_encryption(self, security_config, milvus_config):
        """Test vector data encryption."""
        with patch('ai_prishtina_milvus_client.security.Fernet') as mock_fernet:
            
            # Mock Fernet encryption
            mock_fernet_instance = MagicMock()
            mock_fernet_instance.encrypt.return_value = b"encrypted_vector"
            mock_fernet_instance.decrypt.return_value = b'[0.1, 0.2, 0.3]'
            mock_fernet.return_value = mock_fernet_instance
            
            encryption_manager = EncryptionManager(security_config)
            await encryption_manager.initialize()
            
            # Test vector encryption
            vectors = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
            encrypted_vectors = await encryption_manager.encrypt_vectors(vectors)
            
            # Verify encryption was called for each vector
            assert mock_fernet_instance.encrypt.call_count == 2
            
            # Test vector decryption
            decrypted_vectors = await encryption_manager.decrypt_vectors(encrypted_vectors)
            
            # Verify decryption was called
            assert mock_fernet_instance.decrypt.call_count == 2

    @pytest.mark.asyncio
    async def test_authentication_manager(self, security_config, milvus_config):
        """Test authentication manager functionality."""
        with patch('ai_prishtina_milvus_client.security.jwt') as mock_jwt:
            
            # Mock JWT operations
            mock_jwt.encode.return_value = "mock_jwt_token"
            mock_jwt.decode.return_value = {
                "user_id": "test_user",
                "exp": 1234567890,
                "permissions": ["read", "write"]
            }
            
            auth_manager = AuthenticationManager(security_config)
            await auth_manager.initialize()
            
            # Test user authentication
            credentials = {"username": "test_user", "password": "test_password"}
            auth_result = await auth_manager.authenticate_user(credentials)
            
            assert auth_result["success"] is True
            assert "token" in auth_result
            assert auth_result["user_id"] == "test_user"
            
            # Test token validation
            token = auth_result["token"]
            validation_result = await auth_manager.validate_token(token)
            
            assert validation_result["valid"] is True
            assert validation_result["user_id"] == "test_user"
            assert "read" in validation_result["permissions"]
            assert "write" in validation_result["permissions"]

    @pytest.mark.asyncio
    async def test_authentication_failure_handling(self, security_config, milvus_config):
        """Test authentication failure handling."""
        auth_manager = AuthenticationManager(security_config)
        await auth_manager.initialize()
        
        # Test invalid credentials
        invalid_credentials = {"username": "invalid_user", "password": "wrong_password"}
        
        # Mock failed authentication
        with patch.object(auth_manager, '_verify_credentials', return_value=False):
            auth_result = await auth_manager.authenticate_user(invalid_credentials)
            
            assert auth_result["success"] is False
            assert "error" in auth_result
        
        # Test rate limiting after multiple failures
        for _ in range(security_config.max_login_attempts + 1):
            await auth_manager.authenticate_user(invalid_credentials)
        
        # Should be rate limited now
        auth_result = await auth_manager.authenticate_user(invalid_credentials)
        assert "rate_limited" in auth_result

    @pytest.mark.asyncio
    async def test_access_control_manager(self, security_config, milvus_config):
        """Test access control manager functionality."""
        access_control = AccessControlManager(security_config)
        await access_control.initialize()
        
        # Test permission checking
        user_permissions = ["read", "write"]
        
        # Test allowed operations
        assert await access_control.check_permission(user_permissions, "read") is True
        assert await access_control.check_permission(user_permissions, "write") is True
        
        # Test denied operations
        assert await access_control.check_permission(user_permissions, "admin") is False
        assert await access_control.check_permission(user_permissions, "delete") is False
        
        # Test resource-based access control
        resource_permissions = {
            "collection:test_collection": ["read", "write"],
            "collection:admin_collection": ["admin"]
        }
        
        # Test collection access
        assert await access_control.check_resource_access(
            user_permissions, "collection:test_collection", "read"
        ) is True
        
        assert await access_control.check_resource_access(
            user_permissions, "collection:admin_collection", "admin"
        ) is False

    @pytest.mark.asyncio
    async def test_role_based_access_control(self, security_config, milvus_config):
        """Test role-based access control."""
        access_control = AccessControlManager(security_config)
        await access_control.initialize()
        
        # Define roles and permissions
        roles = {
            "viewer": ["read"],
            "editor": ["read", "write"],
            "admin": ["read", "write", "delete", "admin"]
        }
        
        # Test role assignment
        await access_control.assign_role("user1", "viewer")
        await access_control.assign_role("user2", "editor")
        await access_control.assign_role("user3", "admin")
        
        # Test role-based permissions
        user1_permissions = await access_control.get_user_permissions("user1")
        assert user1_permissions == ["read"]
        
        user2_permissions = await access_control.get_user_permissions("user2")
        assert set(user2_permissions) == {"read", "write"}
        
        user3_permissions = await access_control.get_user_permissions("user3")
        assert set(user3_permissions) == {"read", "write", "delete", "admin"}

    @pytest.mark.asyncio
    async def test_audit_logger(self, security_config, milvus_config):
        """Test audit logging functionality."""
        with patch('builtins.open', create=True) as mock_open, \
             patch('ai_prishtina_milvus_client.security.datetime') as mock_datetime:
            
            # Mock file operations
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            # Mock datetime
            mock_datetime.now.return_value.isoformat.return_value = "2023-01-01T00:00:00"
            
            audit_logger = AuditLogger(security_config)
            await audit_logger.initialize()
            
            # Test audit logging
            await audit_logger.log_event(
                event_type="authentication",
                user_id="test_user",
                action="login",
                resource="system",
                result="success",
                details={"ip_address": "192.168.1.1"}
            )
            
            # Verify file was opened for writing
            mock_open.assert_called()
            mock_file.write.assert_called()
            
            # Verify log format
            written_content = mock_file.write.call_args[0][0]
            log_entry = json.loads(written_content)
            
            assert log_entry["event_type"] == "authentication"
            assert log_entry["user_id"] == "test_user"
            assert log_entry["action"] == "login"
            assert log_entry["result"] == "success"
            assert log_entry["details"]["ip_address"] == "192.168.1.1"

    @pytest.mark.asyncio
    async def test_security_event_monitoring(self, security_config, milvus_config):
        """Test security event monitoring."""
        with patch('builtins.open', create=True):
            
            audit_logger = AuditLogger(security_config)
            await audit_logger.initialize()
            
            # Test multiple security events
            events = [
                {
                    "event_type": "authentication",
                    "user_id": "user1",
                    "action": "login",
                    "result": "success"
                },
                {
                    "event_type": "authentication",
                    "user_id": "user2",
                    "action": "login",
                    "result": "failure"
                },
                {
                    "event_type": "data_access",
                    "user_id": "user1",
                    "action": "search",
                    "resource": "collection:test_collection",
                    "result": "success"
                },
                {
                    "event_type": "data_modification",
                    "user_id": "user1",
                    "action": "insert",
                    "resource": "collection:test_collection",
                    "result": "success"
                }
            ]
            
            # Log all events
            for event in events:
                await audit_logger.log_event(**event)
            
            # Test security metrics
            metrics = await audit_logger.get_security_metrics()
            
            assert metrics["total_events"] == 4
            assert metrics["authentication_events"] == 2
            assert metrics["failed_authentications"] == 1
            assert metrics["data_access_events"] == 1
            assert metrics["data_modification_events"] == 1

    @pytest.mark.asyncio
    async def test_secure_data_operations(self, security_config, milvus_config):
        """Test secure data operations integration."""
        with patch('ai_prishtina_milvus_client.security.Fernet') as mock_fernet, \
             patch('builtins.open', create=True):
            
            # Mock encryption
            mock_fernet_instance = MagicMock()
            mock_fernet_instance.encrypt.return_value = b"encrypted_data"
            mock_fernet_instance.decrypt.return_value = b"decrypted_data"
            mock_fernet.return_value = mock_fernet_instance
            
            manager = SecurityManager(
                security_config=security_config,
                milvus_config=milvus_config
            )
            
            await manager.initialize()
            
            # Test secure insert operation
            vectors = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
            metadata = [{"id": 1, "text": "sensitive data 1"}, {"id": 2, "text": "sensitive data 2"}]
            user_token = "valid_user_token"
            
            # Mock token validation
            with patch.object(manager.auth_manager, 'validate_token') as mock_validate:
                mock_validate.return_value = {
                    "valid": True,
                    "user_id": "test_user",
                    "permissions": ["read", "write"]
                }
                
                # Test secure insert
                result = await manager.secure_insert(
                    vectors=vectors,
                    metadata=metadata,
                    user_token=user_token
                )
                
                assert result["success"] is True
                assert "encrypted_vectors" in result
                assert "audit_logged" in result
                
                # Verify encryption was called
                mock_fernet_instance.encrypt.assert_called()
                
                # Verify token validation
                mock_validate.assert_called_with(user_token)

    @pytest.mark.asyncio
    async def test_security_policy_enforcement(self, security_config, milvus_config):
        """Test security policy enforcement."""
        manager = SecurityManager(
            security_config=security_config,
            milvus_config=milvus_config
        )
        
        await manager.initialize()
        
        # Define security policies
        policies = {
            "data_classification": {
                "public": {"encryption_required": False, "access_level": "all"},
                "internal": {"encryption_required": True, "access_level": "employees"},
                "confidential": {"encryption_required": True, "access_level": "authorized"}
            },
            "operation_restrictions": {
                "bulk_operations": {"max_batch_size": 1000, "rate_limit": "100/hour"},
                "search_operations": {"max_results": 100, "rate_limit": "1000/hour"}
            }
        }
        
        await manager.set_security_policies(policies)
        
        # Test policy enforcement
        data_classification = "confidential"
        operation_type = "bulk_insert"
        batch_size = 500
        
        policy_check = await manager.check_security_policy(
            data_classification=data_classification,
            operation_type=operation_type,
            batch_size=batch_size
        )
        
        assert policy_check["allowed"] is True
        assert policy_check["encryption_required"] is True
        assert policy_check["access_level"] == "authorized"
        
        # Test policy violation
        large_batch_size = 2000
        policy_violation = await manager.check_security_policy(
            data_classification=data_classification,
            operation_type=operation_type,
            batch_size=large_batch_size
        )
        
        assert policy_violation["allowed"] is False
        assert "batch_size_exceeded" in policy_violation["violations"]

    @pytest.mark.asyncio
    async def test_security_incident_response(self, security_config, milvus_config):
        """Test security incident response."""
        with patch('builtins.open', create=True):
            
            manager = SecurityManager(
                security_config=security_config,
                milvus_config=milvus_config
            )
            
            await manager.initialize()
            
            # Simulate security incidents
            incidents = [
                {
                    "type": "unauthorized_access",
                    "severity": "high",
                    "user_id": "suspicious_user",
                    "details": {"attempted_resource": "admin_collection", "ip": "192.168.1.100"}
                },
                {
                    "type": "brute_force_attack",
                    "severity": "critical",
                    "user_id": "attacker",
                    "details": {"failed_attempts": 50, "ip": "10.0.0.1"}
                },
                {
                    "type": "data_exfiltration_attempt",
                    "severity": "critical",
                    "user_id": "insider_threat",
                    "details": {"large_query": True, "data_volume": "10GB"}
                }
            ]
            
            # Process incidents
            for incident in incidents:
                response = await manager.handle_security_incident(incident)
                
                assert "incident_id" in response
                assert response["status"] == "processed"
                assert "actions_taken" in response
                
                # Verify appropriate response based on severity
                if incident["severity"] == "critical":
                    assert "user_suspended" in response["actions_taken"]
                    assert "admin_notified" in response["actions_taken"]
            
            # Test incident summary
            incident_summary = await manager.get_incident_summary()
            
            assert incident_summary["total_incidents"] == 3
            assert incident_summary["critical_incidents"] == 2
            assert incident_summary["high_incidents"] == 1
