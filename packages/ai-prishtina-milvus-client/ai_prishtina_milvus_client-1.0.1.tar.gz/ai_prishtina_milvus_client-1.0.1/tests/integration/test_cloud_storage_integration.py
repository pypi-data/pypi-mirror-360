"""
Integration tests for cloud storage operations using Docker containers (MinIO).

Copyright (c) 2025 Alban Maxhuni <alban.q.maxhuni@gmail.com>

This software is dual-licensed under AGPL-3.0 (open-source) and Commercial licenses.
For commercial licensing, contact: alban.q.maxhuni@gmail.com
"""

import pytest
import asyncio
import json
import tempfile
import os
from typing import List, Dict, Any
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from ai_prishtina_milvus_client.cloud_storage import CloudStorageManager, CloudStorageConfig
from ai_prishtina_milvus_client.exceptions import CloudStorageError


@pytest.mark.integration
@pytest.mark.docker
class TestCloudStorageIntegration:
    """Integration tests for cloud storage operations using MinIO."""

    @pytest.fixture
    def s3_client(self, docker_services, minio_config):
        """S3 client configured for MinIO."""
        client = boto3.client(
            's3',
            endpoint_url=minio_config["endpoint_url"],
            aws_access_key_id=minio_config["access_key"],
            aws_secret_access_key=minio_config["secret_key"],
            region_name='us-east-1'
        )
        
        # Create test bucket
        try:
            client.create_bucket(Bucket=minio_config["bucket_name"])
        except ClientError as e:
            if e.response['Error']['Code'] != 'BucketAlreadyOwnedByYou':
                raise
        
        yield client
        
        # Cleanup: Delete all objects and bucket
        try:
            # List and delete all objects
            response = client.list_objects_v2(Bucket=minio_config["bucket_name"])
            if 'Contents' in response:
                objects = [{'Key': obj['Key']} for obj in response['Contents']]
                client.delete_objects(
                    Bucket=minio_config["bucket_name"],
                    Delete={'Objects': objects}
                )
            
            # Delete bucket
            client.delete_bucket(Bucket=minio_config["bucket_name"])
        except ClientError:
            pass

    @pytest.fixture
    def cloud_storage_config(self, minio_config):
        """Cloud storage configuration."""
        return CloudStorageConfig(
            provider="s3",
            endpoint_url=minio_config["endpoint_url"],
            access_key=minio_config["access_key"],
            secret_key=minio_config["secret_key"],
            bucket_name=minio_config["bucket_name"],
            region="us-east-1"
        )

    @pytest.mark.asyncio
    async def test_basic_storage_operations(self, docker_services, s3_client, minio_config):
        """Test basic storage operations."""
        bucket_name = minio_config["bucket_name"]
        
        # Test file upload
        test_content = "This is a test file for cloud storage integration."
        test_key = "test_files/basic_test.txt"
        
        s3_client.put_object(
            Bucket=bucket_name,
            Key=test_key,
            Body=test_content.encode('utf-8'),
            ContentType='text/plain'
        )
        
        # Test file download
        response = s3_client.get_object(Bucket=bucket_name, Key=test_key)
        downloaded_content = response['Body'].read().decode('utf-8')
        assert downloaded_content == test_content
        
        # Test file listing
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix="test_files/")
        assert 'Contents' in response
        assert len(response['Contents']) == 1
        assert response['Contents'][0]['Key'] == test_key
        
        # Test file deletion
        s3_client.delete_object(Bucket=bucket_name, Key=test_key)
        
        # Verify deletion
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix="test_files/")
        assert 'Contents' not in response

    @pytest.mark.asyncio
    async def test_vector_data_storage(self, docker_services, s3_client, minio_config, sample_vectors, sample_metadata):
        """Test storing and retrieving vector data."""
        bucket_name = minio_config["bucket_name"]
        
        # Prepare vector data
        vector_data = {
            "vectors": sample_vectors,
            "metadata": sample_metadata,
            "collection_info": {
                "name": "test_collection",
                "dimension": 128,
                "total_vectors": len(sample_vectors),
                "created_at": "2023-01-01T00:00:00Z"
            }
        }
        
        # Store vector data as JSON
        vector_key = "vectors/collection_backup_20230101.json"
        s3_client.put_object(
            Bucket=bucket_name,
            Key=vector_key,
            Body=json.dumps(vector_data).encode('utf-8'),
            ContentType='application/json',
            Metadata={
                'collection-name': 'test_collection',
                'vector-count': str(len(sample_vectors)),
                'backup-type': 'full'
            }
        )
        
        # Retrieve and verify vector data
        response = s3_client.get_object(Bucket=bucket_name, Key=vector_key)
        retrieved_data = json.loads(response['Body'].read().decode('utf-8'))
        
        assert len(retrieved_data["vectors"]) == len(sample_vectors)
        assert len(retrieved_data["metadata"]) == len(sample_metadata)
        assert retrieved_data["collection_info"]["name"] == "test_collection"
        
        # Verify metadata
        head_response = s3_client.head_object(Bucket=bucket_name, Key=vector_key)
        assert head_response['Metadata']['collection-name'] == 'test_collection'
        assert head_response['Metadata']['vector-count'] == str(len(sample_vectors))

    @pytest.mark.asyncio
    async def test_large_file_upload(self, docker_services, s3_client, minio_config):
        """Test uploading large files using multipart upload."""
        bucket_name = minio_config["bucket_name"]
        
        # Create a large temporary file (5MB)
        large_data = b"0" * (5 * 1024 * 1024)  # 5MB of zeros
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(large_data)
            temp_file_path = temp_file.name
        
        try:
            # Upload large file
            large_file_key = "large_files/test_large_file.bin"
            
            with open(temp_file_path, 'rb') as file_obj:
                s3_client.upload_fileobj(
                    file_obj,
                    bucket_name,
                    large_file_key,
                    ExtraArgs={
                        'ContentType': 'application/octet-stream',
                        'Metadata': {
                            'file-size': str(len(large_data)),
                            'upload-type': 'multipart'
                        }
                    }
                )
            
            # Verify upload
            head_response = s3_client.head_object(Bucket=bucket_name, Key=large_file_key)
            assert head_response['ContentLength'] == len(large_data)
            
            # Download and verify content
            with tempfile.NamedTemporaryFile() as download_file:
                s3_client.download_fileobj(bucket_name, large_file_key, download_file)
                download_file.seek(0)
                downloaded_data = download_file.read()
                assert len(downloaded_data) == len(large_data)
                assert downloaded_data == large_data
            
        finally:
            # Cleanup
            os.unlink(temp_file_path)
            try:
                s3_client.delete_object(Bucket=bucket_name, Key=large_file_key)
            except ClientError:
                pass

    @pytest.mark.asyncio
    async def test_batch_operations(self, docker_services, s3_client, minio_config):
        """Test batch upload and download operations."""
        bucket_name = minio_config["bucket_name"]
        
        # Create multiple test files
        test_files = {}
        for i in range(10):
            key = f"batch_test/file_{i:03d}.txt"
            content = f"This is test file number {i} for batch operations."
            test_files[key] = content
        
        # Batch upload
        for key, content in test_files.items():
            s3_client.put_object(
                Bucket=bucket_name,
                Key=key,
                Body=content.encode('utf-8'),
                ContentType='text/plain'
            )
        
        # Verify all files were uploaded
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix="batch_test/")
        assert 'Contents' in response
        assert len(response['Contents']) == 10
        
        # Batch download and verify
        for obj in response['Contents']:
            key = obj['Key']
            response = s3_client.get_object(Bucket=bucket_name, Key=key)
            downloaded_content = response['Body'].read().decode('utf-8')
            assert downloaded_content == test_files[key]
        
        # Batch delete
        objects_to_delete = [{'Key': key} for key in test_files.keys()]
        s3_client.delete_objects(
            Bucket=bucket_name,
            Delete={'Objects': objects_to_delete}
        )
        
        # Verify deletion
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix="batch_test/")
        assert 'Contents' not in response

    @pytest.mark.asyncio
    async def test_versioning_and_lifecycle(self, docker_services, s3_client, minio_config):
        """Test object versioning and lifecycle management."""
        bucket_name = minio_config["bucket_name"]
        
        # Note: MinIO supports versioning, but it needs to be enabled
        # For this test, we'll simulate versioning by using different keys
        
        base_key = "versioned_data/config.json"
        
        # Upload multiple versions
        versions = []
        for version in range(1, 4):
            versioned_key = f"{base_key}.v{version}"
            config_data = {
                "version": version,
                "settings": {
                    "max_connections": 100 * version,
                    "timeout": 30 + version,
                    "debug": version == 1
                },
                "updated_at": f"2023-01-0{version}T00:00:00Z"
            }
            
            s3_client.put_object(
                Bucket=bucket_name,
                Key=versioned_key,
                Body=json.dumps(config_data).encode('utf-8'),
                ContentType='application/json',
                Metadata={
                    'version': str(version),
                    'config-type': 'application-config'
                }
            )
            versions.append(versioned_key)
        
        # Verify all versions exist
        for versioned_key in versions:
            response = s3_client.get_object(Bucket=bucket_name, Key=versioned_key)
            config_data = json.loads(response['Body'].read().decode('utf-8'))
            version_num = int(versioned_key.split('.v')[1])
            assert config_data["version"] == version_num
        
        # Simulate lifecycle: keep only latest 2 versions
        # Delete oldest version
        s3_client.delete_object(Bucket=bucket_name, Key=versions[0])
        
        # Verify only 2 versions remain
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix="versioned_data/")
        assert 'Contents' in response
        assert len(response['Contents']) == 2

    @pytest.mark.asyncio
    async def test_cloud_storage_manager(self, docker_services, cloud_storage_config, sample_vectors):
        """Test CloudStorageManager integration."""
        # Note: This assumes CloudStorageManager exists in the codebase
        # If it doesn't, this test will be skipped or mocked
        
        try:
            manager = CloudStorageManager(cloud_storage_config)
            
            # Test upload
            test_data = {
                "vectors": sample_vectors[:5],
                "metadata": [{"id": i} for i in range(5)],
                "timestamp": "2023-01-01T00:00:00Z"
            }
            
            upload_result = await manager.upload_data(
                key="manager_test/test_data.json",
                data=test_data,
                content_type="application/json"
            )
            
            assert upload_result["success"] is True
            assert "key" in upload_result
            
            # Test download
            download_result = await manager.download_data("manager_test/test_data.json")
            
            assert download_result["success"] is True
            assert len(download_result["data"]["vectors"]) == 5
            
            # Test list
            list_result = await manager.list_objects(prefix="manager_test/")
            
            assert list_result["success"] is True
            assert len(list_result["objects"]) == 1
            
            # Test delete
            delete_result = await manager.delete_data("manager_test/test_data.json")
            
            assert delete_result["success"] is True
            
        except ImportError:
            pytest.skip("CloudStorageManager not available")

    @pytest.mark.asyncio
    async def test_error_handling(self, docker_services, s3_client, minio_config):
        """Test error handling scenarios."""
        bucket_name = minio_config["bucket_name"]
        
        # Test accessing non-existent object
        with pytest.raises(ClientError) as exc_info:
            s3_client.get_object(Bucket=bucket_name, Key="non_existent_file.txt")
        
        assert exc_info.value.response['Error']['Code'] == 'NoSuchKey'
        
        # Test uploading to non-existent bucket
        with pytest.raises(ClientError):
            s3_client.put_object(
                Bucket="non-existent-bucket-12345",
                Key="test.txt",
                Body=b"test content"
            )
        
        # Test invalid operations
        with pytest.raises(ClientError):
            # Try to delete non-existent object (this might not raise error in some cases)
            s3_client.delete_object(Bucket=bucket_name, Key="non_existent_file.txt")

    @pytest.mark.asyncio
    async def test_performance_monitoring(self, docker_services, s3_client, minio_config):
        """Test storage performance monitoring."""
        import time
        
        bucket_name = minio_config["bucket_name"]
        
        # Test upload performance
        test_sizes = [1024, 10240, 102400]  # 1KB, 10KB, 100KB
        performance_metrics = {}
        
        for size in test_sizes:
            test_data = b"0" * size
            key = f"performance_test/file_{size}_bytes.bin"
            
            # Measure upload time
            start_time = time.time()
            s3_client.put_object(
                Bucket=bucket_name,
                Key=key,
                Body=test_data,
                ContentType='application/octet-stream'
            )
            upload_time = time.time() - start_time
            
            # Measure download time
            start_time = time.time()
            response = s3_client.get_object(Bucket=bucket_name, Key=key)
            downloaded_data = response['Body'].read()
            download_time = time.time() - start_time
            
            # Verify data integrity
            assert len(downloaded_data) == size
            assert downloaded_data == test_data
            
            # Store metrics
            performance_metrics[size] = {
                "upload_time": upload_time,
                "download_time": download_time,
                "upload_speed": size / upload_time if upload_time > 0 else 0,
                "download_speed": size / download_time if download_time > 0 else 0
            }
        
        # Verify performance is reasonable
        for size, metrics in performance_metrics.items():
            assert metrics["upload_time"] > 0
            assert metrics["download_time"] > 0
            assert metrics["upload_speed"] > 0
            assert metrics["download_speed"] > 0
            
            # Log performance (in real scenario, send to monitoring)
            print(f"Size: {size} bytes")
            print(f"  Upload: {metrics['upload_time']:.4f}s ({metrics['upload_speed']:.0f} B/s)")
            print(f"  Download: {metrics['download_time']:.4f}s ({metrics['download_speed']:.0f} B/s)")
