"""
Module: data_management_example.py

Copyright (c) 2025 Alban Maxhuni <alban.q.maxhuni@gmail.com>

This software is dual-licensed under AGPL-3.0 (open-source) and Commercial licenses.
For commercial licensing, contact: alban.q.maxhuni@gmail.com
"""

from ai_prishtina_milvus_client import DataManager, DataValidationConfig

data = [{"id": 1, "text": "hello"}, {"id": 2, "text": "world"}]
validation_config = DataValidationConfig(required_fields=["id", "text"], field_types={"id": int, "text": str})
manager = DataManager()
valid_data, errors = manager.validate_data(data, validation_config)
print("Valid data:", valid_data)
print("Errors:", errors) 