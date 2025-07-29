#!/usr/bin/env python3
"""
Integration test runner script.

This script provides a convenient way to run integration tests with proper
Docker container management and comprehensive reporting.
"""

import argparse
import asyncio
import os
import subprocess
import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Optional


class IntegrationTestRunner:
    """Integration test runner with Docker management."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.integration_dir = Path(__file__).parent
        self.docker_compose_file = None
        self.services_started = False
        
    def setup_environment(self):
        """Setup test environment variables."""
        env_vars = {
            "PYTHONPATH": str(self.project_root),
            "INTEGRATION_TEST_MODE": "true",
            "LOG_LEVEL": "INFO"
        }
        
        for key, value in env_vars.items():
            os.environ[key] = value
            
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are available."""
        print("🔍 Checking prerequisites...")
        
        # Check Docker
        try:
            result = subprocess.run(["docker", "--version"], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ Docker: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Docker not found. Please install Docker.")
            return False
            
        # Check Docker Compose
        try:
            result = subprocess.run(["docker-compose", "--version"], 
                                  capture_output=True, text=True, check=True)
            print(f"✅ Docker Compose: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Docker Compose not found. Please install Docker Compose.")
            return False
            
        # Check Python packages
        required_packages = [
            "pytest", "pytest-asyncio", "pytest-cov", 
            "docker", "redis", "boto3", "requests", "aiokafka"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                print(f"✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"❌ {package}")
                
        if missing_packages:
            print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
            print("Install with: pip install " + " ".join(missing_packages))
            return False
            
        return True
        
    def start_services(self, services: Optional[List[str]] = None) -> bool:
        """Start Docker services."""
        print("🚀 Starting Docker services...")
        
        # Create temporary docker-compose file
        compose_content = self._get_docker_compose_content()
        
        import tempfile
        import yaml
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(compose_content, f)
            self.docker_compose_file = f.name
            
        try:
            # Start services
            cmd = ["docker-compose", "-f", self.docker_compose_file, "up", "-d"]
            if services:
                cmd.extend(services)
                
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print("✅ Services started successfully")
            
            # Wait for services to be healthy
            if self._wait_for_services():
                self.services_started = True
                return True
            else:
                print("❌ Services failed to become healthy")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start services: {e.stderr}")
            return False
            
    def _get_docker_compose_content(self) -> Dict:
        """Get Docker Compose configuration."""
        return {
            "version": "3.8",
            "services": {
                "redis": {
                    "image": "redis:7-alpine",
                    "ports": ["6379:6379"],
                    "command": "redis-server --appendonly yes",
                    "healthcheck": {
                        "test": ["CMD", "redis-cli", "ping"],
                        "interval": "5s",
                        "timeout": "3s",
                        "retries": 5
                    }
                },
                "kafka": {
                    "image": "confluentinc/cp-kafka:latest",
                    "ports": ["9092:9092"],
                    "environment": {
                        "KAFKA_BROKER_ID": "1",
                        "KAFKA_ZOOKEEPER_CONNECT": "zookeeper:2181",
                        "KAFKA_ADVERTISED_LISTENERS": "PLAINTEXT://localhost:9092",
                        "KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR": "1",
                        "KAFKA_AUTO_CREATE_TOPICS_ENABLE": "true"
                    },
                    "depends_on": ["zookeeper"]
                },
                "zookeeper": {
                    "image": "confluentinc/cp-zookeeper:latest",
                    "ports": ["2181:2181"],
                    "environment": {
                        "ZOOKEEPER_CLIENT_PORT": "2181",
                        "ZOOKEEPER_TICK_TIME": "2000"
                    }
                },
                "minio": {
                    "image": "minio/minio:latest",
                    "ports": ["9000:9000", "9001:9001"],
                    "environment": {
                        "MINIO_ROOT_USER": "minioadmin",
                        "MINIO_ROOT_PASSWORD": "minioadmin"
                    },
                    "command": "server /data --console-address ':9001'"
                },
                "prometheus": {
                    "image": "prom/prometheus:latest",
                    "ports": ["9090:9090"]
                },
                "pushgateway": {
                    "image": "prom/pushgateway:latest",
                    "ports": ["9091:9091"]
                },
                "mailhog": {
                    "image": "mailhog/mailhog:latest",
                    "ports": ["1025:1025", "8025:8025"]
                },
                "etcd": {
                    "image": "quay.io/coreos/etcd:v3.5.5",
                    "ports": ["2379:2379"],
                    "environment": {
                        "ETCD_AUTO_COMPACTION_MODE": "revision",
                        "ETCD_AUTO_COMPACTION_RETENTION": "1000",
                        "ETCD_QUOTA_BACKEND_BYTES": "4294967296"
                    },
                    "command": "etcd -advertise-client-urls=http://127.0.0.1:2379 -listen-client-urls http://0.0.0.0:2379 --data-dir /etcd"
                },
                "milvus": {
                    "image": "milvusdb/milvus:v2.3.3",
                    "ports": ["19530:19530"],
                    "environment": {
                        "ETCD_ENDPOINTS": "etcd:2379",
                        "MINIO_ADDRESS": "minio:9000"
                    },
                    "command": ["milvus", "run", "standalone"],
                    "depends_on": ["etcd", "minio"]
                }
            }
        }
        
    def _wait_for_services(self, timeout: int = 120) -> bool:
        """Wait for services to become healthy."""
        print("⏳ Waiting for services to become healthy...")
        
        services_to_check = [
            ("Redis", "localhost", 6379),
            ("MinIO", "localhost", 9000),
            ("Prometheus", "localhost", 9090),
            ("Pushgateway", "localhost", 9091),
            ("MailHog", "localhost", 1025),
            ("Milvus", "localhost", 19530)
        ]
        
        start_time = time.time()
        
        for service_name, host, port in services_to_check:
            print(f"  Checking {service_name}...")
            
            while time.time() - start_time < timeout:
                try:
                    import socket
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex((host, port))
                    sock.close()
                    
                    if result == 0:
                        print(f"  ✅ {service_name} is ready")
                        break
                except Exception:
                    pass
                    
                time.sleep(2)
            else:
                print(f"  ❌ {service_name} failed to start within {timeout} seconds")
                return False
                
        print("✅ All services are healthy")
        return True
        
    def run_tests(self, test_args: List[str]) -> bool:
        """Run integration tests."""
        print("🧪 Running integration tests...")
        
        # Build pytest command
        cmd = ["python", "-m", "pytest", str(self.integration_dir)]
        cmd.extend(test_args)
        
        # Add default arguments if none provided
        if not any(arg.startswith("-") for arg in test_args):
            cmd.extend(["-v", "--tb=short"])
            
        print(f"Command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, cwd=self.project_root)
            return result.returncode == 0
        except KeyboardInterrupt:
            print("\n⚠️ Tests interrupted by user")
            return False
            
    def stop_services(self):
        """Stop Docker services."""
        if self.services_started and self.docker_compose_file:
            print("🛑 Stopping Docker services...")
            
            try:
                subprocess.run([
                    "docker-compose", "-f", self.docker_compose_file, 
                    "down", "-v"
                ], capture_output=True, check=True)
                print("✅ Services stopped successfully")
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Error stopping services: {e.stderr}")
                
            # Clean up temporary file
            try:
                os.unlink(self.docker_compose_file)
            except OSError:
                pass
                
    def generate_report(self, success: bool):
        """Generate test report."""
        print("\n" + "="*60)
        print("📊 INTEGRATION TEST REPORT")
        print("="*60)
        
        if success:
            print("✅ All tests passed successfully!")
        else:
            print("❌ Some tests failed.")
            
        print("\n📋 Test Coverage:")
        print("  • Milvus vector database operations")
        print("  • Redis caching and streaming")
        print("  • Kafka message processing")
        print("  • MinIO/S3 cloud storage")
        print("  • Prometheus monitoring")
        print("  • End-to-end workflows")
        
        print("\n🔗 Service URLs (while running):")
        print("  • Milvus: localhost:19530")
        print("  • Redis: localhost:6379")
        print("  • Kafka: localhost:9092")
        print("  • MinIO Console: http://localhost:9001")
        print("  • Prometheus: http://localhost:9090")
        print("  • MailHog UI: http://localhost:8025")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run integration tests for AI Prishtina Milvus Client"
    )
    
    parser.add_argument(
        "--services", 
        nargs="+", 
        help="Specific services to start (default: all)"
    )
    
    parser.add_argument(
        "--no-cleanup", 
        action="store_true",
        help="Don't stop services after tests (for debugging)"
    )
    
    parser.add_argument(
        "--check-only", 
        action="store_true",
        help="Only check prerequisites, don't run tests"
    )
    
    # Pass through pytest arguments
    parser.add_argument(
        "pytest_args", 
        nargs="*", 
        help="Additional arguments to pass to pytest"
    )
    
    args = parser.parse_args()
    
    runner = IntegrationTestRunner()
    
    print("🚀 AI Prishtina Milvus Client - Integration Test Runner")
    print("="*60)
    
    # Setup environment
    runner.setup_environment()
    
    # Check prerequisites
    if not runner.check_prerequisites():
        sys.exit(1)
        
    if args.check_only:
        print("✅ All prerequisites satisfied!")
        sys.exit(0)
        
    success = False
    
    try:
        # Start services
        if not runner.start_services(args.services):
            sys.exit(1)
            
        # Run tests
        success = runner.run_tests(args.pytest_args)
        
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
        
    finally:
        # Cleanup
        if not args.no_cleanup:
            runner.stop_services()
        else:
            print("⚠️ Services left running (--no-cleanup specified)")
            
        # Generate report
        runner.generate_report(success)
        
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
