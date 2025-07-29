"""
Integration tests for monitoring systems using Docker containers (Prometheus).

Copyright (c) 2025 Alban Maxhuni <alban.q.maxhuni@gmail.com>

This software is dual-licensed under AGPL-3.0 (open-source) and Commercial licenses.
For commercial licensing, contact: alban.q.maxhuni@gmail.com
"""

import pytest
import asyncio
import time
import json
import requests
from typing import List, Dict, Any

from ai_prishtina_milvus_client.monitoring import MonitoringManager, MetricsConfig
from ai_prishtina_milvus_client.exceptions import MonitoringError


@pytest.mark.integration
@pytest.mark.docker
class TestMonitoringIntegration:
    """Integration tests for monitoring operations."""

    @pytest.fixture
    def metrics_config(self, prometheus_config):
        """Metrics configuration for testing."""
        return MetricsConfig(
            prometheus_url=prometheus_config["prometheus_url"],
            pushgateway_url=prometheus_config["pushgateway_url"],
            job_name="ai_prishtina_milvus_client_test",
            instance="test_instance",
            push_interval=10,
            enable_system_metrics=True,
            enable_application_metrics=True
        )

    @pytest.mark.asyncio
    async def test_prometheus_connection(self, docker_services, prometheus_config):
        """Test basic Prometheus connection."""
        prometheus_url = prometheus_config["prometheus_url"]
        
        # Test Prometheus health
        response = requests.get(f"{prometheus_url}/-/healthy", timeout=10)
        assert response.status_code == 200
        
        # Test Prometheus ready
        response = requests.get(f"{prometheus_url}/-/ready", timeout=10)
        assert response.status_code == 200
        
        # Test basic query
        response = requests.get(
            f"{prometheus_url}/api/v1/query",
            params={"query": "up"},
            timeout=10
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"

    @pytest.mark.asyncio
    async def test_pushgateway_connection(self, docker_services, prometheus_config):
        """Test Pushgateway connection."""
        pushgateway_url = prometheus_config["pushgateway_url"]
        
        # Test Pushgateway health
        response = requests.get(f"{pushgateway_url}/metrics", timeout=10)
        assert response.status_code == 200
        
        # Push a test metric
        test_metric = """
        # HELP test_metric A test metric for integration testing
        # TYPE test_metric gauge
        test_metric{job="integration_test",instance="test"} 42
        """
                
        response = requests.post(
            f"{pushgateway_url}/metrics/job/integration_test/instance/test",
            data=test_metric,
            headers={"Content-Type": "text/plain"},
            timeout=10
        )
        assert response.status_code == 200
        
        # Verify metric was pushed
        response = requests.get(f"{pushgateway_url}/metrics", timeout=10)
        assert response.status_code == 200
        assert "test_metric" in response.text

    @pytest.mark.asyncio
    async def test_custom_metrics_collection(self, docker_services, metrics_config):
        """Test custom metrics collection and pushing."""
        try:
            manager = MonitoringManager(metrics_config)
            
            # Record various metrics
            await manager.record_counter("vector_inserts_total", 150, {"collection": "test_collection"})
            await manager.record_gauge("active_connections", 25, {"service": "milvus"})
            await manager.record_histogram("query_duration_seconds", 0.045, {"operation": "search"})
            await manager.record_histogram("query_duration_seconds", 0.032, {"operation": "search"})
            await manager.record_histogram("query_duration_seconds", 0.067, {"operation": "search"})
            
            # Push metrics to Pushgateway
            push_result = await manager.push_metrics()
            assert push_result["success"] is True
            
            # Wait a moment for metrics to be available
            await asyncio.sleep(2)
            
            # Verify metrics were pushed
            response = requests.get(f"{metrics_config.pushgateway_url}/metrics", timeout=10)
            assert response.status_code == 200
            metrics_text = response.text
            
            assert "vector_inserts_total" in metrics_text
            assert "active_connections" in metrics_text
            assert "query_duration_seconds" in metrics_text
            
        except ImportError:
            pytest.skip("MonitoringManager not available")

    @pytest.mark.asyncio
    async def test_system_metrics_collection(self, docker_services, metrics_config):
        """Test system metrics collection."""
        try:
            manager = MonitoringManager(metrics_config)
            
            # Collect system metrics
            system_metrics = await manager.collect_system_metrics()
            
            # Verify system metrics
            assert "cpu_usage_percent" in system_metrics
            assert "memory_usage_percent" in system_metrics
            assert "disk_usage_percent" in system_metrics
            assert "network_bytes_sent" in system_metrics
            assert "network_bytes_received" in system_metrics
            
            # Verify values are reasonable
            assert 0 <= system_metrics["cpu_usage_percent"] <= 100
            assert 0 <= system_metrics["memory_usage_percent"] <= 100
            assert 0 <= system_metrics["disk_usage_percent"] <= 100
            assert system_metrics["network_bytes_sent"] >= 0
            assert system_metrics["network_bytes_received"] >= 0
            
            # Push system metrics
            await manager.push_system_metrics()
            
        except ImportError:
            pytest.skip("MonitoringManager not available")

    @pytest.mark.asyncio
    async def test_application_metrics_collection(self, docker_services, metrics_config, sample_vectors):
        """Test application-specific metrics collection."""
        try:
            manager = MonitoringManager(metrics_config)
            
            # Simulate application operations and collect metrics
            operations = [
                {"type": "insert", "vectors": 100, "duration": 0.25, "success": True},
                {"type": "search", "vectors": 1, "duration": 0.045, "success": True},
                {"type": "search", "vectors": 5, "duration": 0.123, "success": True},
                {"type": "insert", "vectors": 50, "duration": 0.15, "success": False},
                {"type": "delete", "vectors": 10, "duration": 0.08, "success": True},
            ]
            
            for op in operations:
                # Record operation metrics
                await manager.record_operation(
                    operation_type=op["type"],
                    duration=op["duration"],
                    vector_count=op["vectors"],
                    success=op["success"]
                )
            
            # Get aggregated metrics
            app_metrics = await manager.get_application_metrics()
            
            # Verify aggregated metrics
            assert app_metrics["total_operations"] == 5
            assert app_metrics["successful_operations"] == 4
            assert app_metrics["failed_operations"] == 1
            assert app_metrics["success_rate"] == 0.8
            assert app_metrics["total_vectors_processed"] == 166
            assert app_metrics["average_operation_duration"] > 0
            
            # Verify operation-specific metrics
            assert "insert" in app_metrics["operations_by_type"]
            assert "search" in app_metrics["operations_by_type"]
            assert "delete" in app_metrics["operations_by_type"]
            
            assert app_metrics["operations_by_type"]["insert"]["count"] == 2
            assert app_metrics["operations_by_type"]["search"]["count"] == 2
            assert app_metrics["operations_by_type"]["delete"]["count"] == 1
            
        except ImportError:
            pytest.skip("MonitoringManager not available")

    @pytest.mark.asyncio
    async def test_alerting_rules(self, docker_services, metrics_config):
        """Test alerting based on metrics thresholds."""
        try:
            manager = MonitoringManager(metrics_config)
            
            # Define alerting rules
            alerting_rules = [
                {
                    "name": "high_error_rate",
                    "condition": "error_rate > 0.1",
                    "threshold": 0.1,
                    "metric": "error_rate",
                    "severity": "warning"
                },
                {
                    "name": "high_latency",
                    "condition": "avg_latency > 1.0",
                    "threshold": 1.0,
                    "metric": "avg_latency",
                    "severity": "critical"
                }
            ]
            
            await manager.configure_alerts(alerting_rules)
            
            # Simulate high error rate
            for _ in range(10):
                await manager.record_operation("search", 0.05, 1, success=False)
            
            for _ in range(5):
                await manager.record_operation("search", 0.05, 1, success=True)
            
            # Check if alerts are triggered
            alerts = await manager.check_alerts()
            
            # Should trigger high error rate alert
            high_error_alerts = [a for a in alerts if a["rule_name"] == "high_error_rate"]
            assert len(high_error_alerts) > 0
            assert high_error_alerts[0]["severity"] == "warning"
            
            # Simulate high latency
            for _ in range(5):
                await manager.record_operation("search", 1.5, 1, success=True)
            
            alerts = await manager.check_alerts()
            
            # Should trigger high latency alert
            high_latency_alerts = [a for a in alerts if a["rule_name"] == "high_latency"]
            assert len(high_latency_alerts) > 0
            assert high_latency_alerts[0]["severity"] == "critical"
            
        except ImportError:
            pytest.skip("MonitoringManager not available")

    @pytest.mark.asyncio
    async def test_metrics_retention_and_cleanup(self, docker_services, metrics_config):
        """Test metrics retention and cleanup policies."""
        try:
            manager = MonitoringManager(metrics_config)
            
            # Generate historical metrics
            current_time = time.time()
            
            # Generate metrics for different time periods
            time_periods = [
                current_time - 3600,  # 1 hour ago
                current_time - 7200,  # 2 hours ago
                current_time - 86400,  # 1 day ago
                current_time - 604800,  # 1 week ago
            ]
            
            for timestamp in time_periods:
                await manager.record_historical_metric(
                    metric_name="test_retention_metric",
                    value=100,
                    timestamp=timestamp,
                    labels={"period": f"t_{int(timestamp)}"}
                )
            
            # Set retention policy (keep metrics for 2 hours)
            retention_policy = {
                "retention_period": 7200,  # 2 hours in seconds
                "cleanup_interval": 3600   # Run cleanup every hour
            }
            
            await manager.set_retention_policy(retention_policy)
            
            # Run cleanup
            cleanup_result = await manager.cleanup_old_metrics()
            
            # Verify cleanup results
            assert cleanup_result["success"] is True
            assert cleanup_result["metrics_deleted"] >= 2  # Should delete 1 day and 1 week old metrics
            
            # Verify remaining metrics
            remaining_metrics = await manager.get_metrics_in_range(
                metric_name="test_retention_metric",
                start_time=current_time - 86400,  # Last 24 hours
                end_time=current_time
            )
            
            # Should only have metrics from last 2 hours
            assert len(remaining_metrics) <= 2
            
        except ImportError:
            pytest.skip("MonitoringManager not available")

    @pytest.mark.asyncio
    async def test_dashboard_data_export(self, docker_services, prometheus_config):
        """Test exporting data for dashboards."""
        prometheus_url = prometheus_config["prometheus_url"]
        
        # Query Prometheus for metrics data
        queries = [
            "up",
            "prometheus_build_info",
            "prometheus_config_last_reload_successful"
        ]
        
        dashboard_data = {}
        
        for query in queries:
            response = requests.get(
                f"{prometheus_url}/api/v1/query",
                params={"query": query},
                timeout=10
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            
            dashboard_data[query] = data["data"]["result"]
        
        # Verify we got data for dashboards
        assert len(dashboard_data) == len(queries)
        
        # Test range queries for time series data
        end_time = int(time.time())
        start_time = end_time - 3600  # Last hour
        
        response = requests.get(
            f"{prometheus_url}/api/v1/query_range",
            params={
                "query": "up",
                "start": start_time,
                "end": end_time,
                "step": "60s"  # 1 minute intervals
            },
            timeout=10
        )
        
        assert response.status_code == 200
        range_data = response.json()
        assert range_data["status"] == "success"
        
        # Verify time series data structure
        if range_data["data"]["result"]:
            time_series = range_data["data"]["result"][0]
            assert "metric" in time_series
            assert "values" in time_series
            assert len(time_series["values"]) > 0

    @pytest.mark.asyncio
    async def test_performance_monitoring(self, docker_services, metrics_config):
        """Test performance monitoring capabilities."""
        try:
            manager = MonitoringManager(metrics_config)
            
            # Simulate various performance scenarios
            scenarios = [
                {"name": "normal_load", "operations": 100, "error_rate": 0.02, "avg_latency": 0.05},
                {"name": "high_load", "operations": 1000, "error_rate": 0.05, "avg_latency": 0.15},
                {"name": "stress_test", "operations": 5000, "error_rate": 0.1, "avg_latency": 0.3},
            ]
            
            performance_results = {}
            
            for scenario in scenarios:
                start_time = time.time()
                
                # Simulate operations
                successful_ops = int(scenario["operations"] * (1 - scenario["error_rate"]))
                failed_ops = scenario["operations"] - successful_ops
                
                # Record successful operations
                for _ in range(successful_ops):
                    latency = scenario["avg_latency"] * (0.8 + 0.4 * time.time() % 1)  # Add some variance
                    await manager.record_operation("test_op", latency, 1, success=True)
                
                # Record failed operations
                for _ in range(failed_ops):
                    latency = scenario["avg_latency"] * 1.5  # Failed ops take longer
                    await manager.record_operation("test_op", latency, 1, success=False)
                
                scenario_duration = time.time() - start_time
                
                # Get performance metrics for this scenario
                perf_metrics = await manager.get_performance_metrics()
                
                performance_results[scenario["name"]] = {
                    "duration": scenario_duration,
                    "throughput": scenario["operations"] / scenario_duration,
                    "actual_error_rate": perf_metrics.get("error_rate", 0),
                    "actual_avg_latency": perf_metrics.get("avg_latency", 0),
                    "p95_latency": perf_metrics.get("p95_latency", 0),
                    "p99_latency": perf_metrics.get("p99_latency", 0)
                }
            
            # Verify performance trends
            assert performance_results["normal_load"]["throughput"] > 0
            assert performance_results["high_load"]["actual_avg_latency"] > performance_results["normal_load"]["actual_avg_latency"]
            assert performance_results["stress_test"]["actual_error_rate"] > performance_results["normal_load"]["actual_error_rate"]
            
        except ImportError:
            pytest.skip("MonitoringManager not available")

    @pytest.mark.asyncio
    async def test_monitoring_error_handling(self, docker_services, prometheus_config):
        """Test monitoring system error handling."""
        # Test connection to non-existent Prometheus
        with pytest.raises(Exception):
            response = requests.get("http://localhost:9999/api/v1/query", timeout=5)
            response.raise_for_status()
        
        # Test invalid queries
        prometheus_url = prometheus_config["prometheus_url"]
        
        response = requests.get(
            f"{prometheus_url}/api/v1/query",
            params={"query": "invalid_metric_name{"},  # Invalid PromQL
            timeout=10
        )
        
        # Should return 400 for invalid query
        assert response.status_code == 400
        
        # Test pushgateway error handling
        pushgateway_url = prometheus_config["pushgateway_url"]
        
        # Try to push invalid metric format
        invalid_metric = "this is not a valid metric format"
        
        response = requests.post(
            f"{pushgateway_url}/metrics/job/error_test",
            data=invalid_metric,
            headers={"Content-Type": "text/plain"},
            timeout=10
        )
        
        # Should handle invalid format gracefully
        # (Pushgateway might accept it but Prometheus will reject during scraping)
