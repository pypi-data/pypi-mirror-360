"""
Module: data_validation_example.py

Copyright (c) 2025 Alban Maxhuni <alban.q.maxhuni@gmail.com>

This software is dual-licensed under AGPL-3.0 (open-source) and Commercial licenses.
For commercial licensing, contact: alban.q.maxhuni@gmail.com
"""

from ai_prishtina_milvus_client import DataValidator, VectorValidationConfig

# Example: Validate and normalize vectors
vectors = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
config = VectorValidationConfig(expected_dim=3, normalize=True)
validated_vectors = DataValidator.validate_vectors(vectors, config)
print("Validated vectors:", validated_vectors) 