"""
Module: dev_tools_example.py

Copyright (c) 2025 Alban Maxhuni <alban.q.maxhuni@gmail.com>

This software is dual-licensed under AGPL-3.0 (open-source) and Commercial licenses.
For commercial licensing, contact: alban.q.maxhuni@gmail.com
"""

from ai_prishtina_milvus_client import DevTools, LoggingConfig

logging_config = LoggingConfig(level="INFO", file_path="dev.log")
tools = DevTools(logging_config)

@tools.debug
def add(a, b):
    return a + b

print(add(2, 3)) 