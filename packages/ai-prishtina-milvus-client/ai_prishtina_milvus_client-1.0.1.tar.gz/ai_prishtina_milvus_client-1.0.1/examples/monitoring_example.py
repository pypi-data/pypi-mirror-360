"""
Module: monitoring_example.py

Copyright (c) 2025 Alban Maxhuni <alban.q.maxhuni@gmail.com>

This software is dual-licensed under AGPL-3.0 (open-source) and Commercial licenses.
For commercial licensing, contact: alban.q.maxhuni@gmail.com
"""

from ai_prishtina_milvus_client import MetricsCollector, MonitoringConfig

client = ...  # Your Milvus client instance
monitoring_config = MonitoringConfig(collect_system_metrics=True)
collector = MetricsCollector(client, monitoring_config)
# system_metrics = collector.collect_system_metrics()
# print(system_metrics)
print("MetricsCollector ready for system metrics collection.") 