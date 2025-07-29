"""
Module: performance_example.py

Copyright (c) 2025 Alban Maxhuni <alban.q.maxhuni@gmail.com>

This software is dual-licensed under AGPL-3.0 (open-source) and Commercial licenses.
For commercial licensing, contact: alban.q.maxhuni@gmail.com
"""

from ai_prishtina_milvus_client import PerformanceOptimizer, CacheConfig

cache_config = CacheConfig(max_size=100, expiry_time=60)
optimizer = PerformanceOptimizer(cache_config)

@optimizer.cached
def expensive_computation(x):
    return x * x

print(expensive_computation(10)) 