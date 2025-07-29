"""
Module: security_example.py

Copyright (c) 2025 Alban Maxhuni <alban.q.maxhuni@gmail.com>

This software is dual-licensed under AGPL-3.0 (open-source) and Commercial licenses.
For commercial licensing, contact: alban.q.maxhuni@gmail.com
"""

from ai_prishtina_milvus_client import SecurityManager, SecurityConfig

security_config = SecurityConfig(secret_key="supersecret", token_expiry=3600)
manager = SecurityManager(security_config)
user = manager.create_user("alice", "password123", ["admin"])
token = manager.authenticate("alice", "password123")
print("JWT Token:", token) 