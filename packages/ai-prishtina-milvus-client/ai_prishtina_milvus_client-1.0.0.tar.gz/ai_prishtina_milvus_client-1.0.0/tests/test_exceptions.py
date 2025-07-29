"""
Tests for custom exceptions.
"""

import pytest
from ai_prishtina_milvus_client.exceptions import (
    MilvusClientError,
    ConfigurationError,
    ConnectionError,
    CollectionError,
    InsertError,
    SearchError,
    IndexError,
    DataSourceError,
    CloudStorageError,
    APIError,
    ValidationError,
    BatchOperationError,
    StreamingError,
    SecurityError,
    MonitoringError,
    PerformanceError,
    DistributedError,
    ErrorRecoveryError,
    DataManagementError,
    AdvancedOperationError,
    DevToolsError,
    MilvusError
)


class TestExceptions:
    """Test custom exception classes."""

    def test_base_exception(self):
        """Test base MilvusClientError."""
        error = MilvusClientError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_configuration_error(self):
        """Test ConfigurationError."""
        error = ConfigurationError("Invalid configuration")
        assert str(error) == "Invalid configuration"
        assert isinstance(error, MilvusClientError)

    def test_connection_error(self):
        """Test ConnectionError."""
        error = ConnectionError("Connection failed")
        assert str(error) == "Connection failed"
        assert isinstance(error, MilvusClientError)

    def test_collection_error(self):
        """Test CollectionError."""
        error = CollectionError("Collection operation failed")
        assert str(error) == "Collection operation failed"
        assert isinstance(error, MilvusClientError)

    def test_insert_error(self):
        """Test InsertError."""
        error = InsertError("Insert operation failed")
        assert str(error) == "Insert operation failed"
        assert isinstance(error, MilvusClientError)

    def test_search_error(self):
        """Test SearchError."""
        error = SearchError("Search operation failed")
        assert str(error) == "Search operation failed"
        assert isinstance(error, MilvusClientError)

    def test_index_error(self):
        """Test IndexError."""
        error = IndexError("Index operation failed")
        assert str(error) == "Index operation failed"
        assert isinstance(error, MilvusClientError)

    def test_data_source_error(self):
        """Test DataSourceError."""
        error = DataSourceError("Data source operation failed")
        assert str(error) == "Data source operation failed"
        assert isinstance(error, MilvusClientError)

    def test_cloud_storage_error(self):
        """Test CloudStorageError."""
        error = CloudStorageError("Cloud storage operation failed")
        assert str(error) == "Cloud storage operation failed"
        assert isinstance(error, MilvusClientError)

    def test_api_error(self):
        """Test APIError."""
        error = APIError("API operation failed")
        assert str(error) == "API operation failed"
        assert isinstance(error, MilvusClientError)

    def test_validation_error(self):
        """Test ValidationError."""
        error = ValidationError("Validation failed")
        assert str(error) == "Validation failed"
        assert isinstance(error, MilvusClientError)

    def test_batch_operation_error(self):
        """Test BatchOperationError."""
        error = BatchOperationError("Batch operation failed")
        assert str(error) == "Batch operation failed"
        assert isinstance(error, MilvusClientError)

    def test_streaming_error(self):
        """Test StreamingError."""
        error = StreamingError("Streaming operation failed")
        assert str(error) == "Streaming operation failed"
        assert isinstance(error, MilvusClientError)

    def test_security_error(self):
        """Test SecurityError."""
        error = SecurityError("Security operation failed")
        assert str(error) == "Security operation failed"
        assert isinstance(error, MilvusClientError)

    def test_monitoring_error(self):
        """Test MonitoringError."""
        error = MonitoringError("Monitoring operation failed")
        assert str(error) == "Monitoring operation failed"
        assert isinstance(error, MilvusClientError)

    def test_performance_error(self):
        """Test PerformanceError."""
        error = PerformanceError("Performance operation failed")
        assert str(error) == "Performance operation failed"
        assert isinstance(error, MilvusClientError)

    def test_distributed_error(self):
        """Test DistributedError."""
        error = DistributedError("Distributed operation failed")
        assert str(error) == "Distributed operation failed"
        assert isinstance(error, MilvusClientError)

    def test_error_recovery_error(self):
        """Test ErrorRecoveryError."""
        error = ErrorRecoveryError("Error recovery failed")
        assert str(error) == "Error recovery failed"
        assert isinstance(error, MilvusClientError)

    def test_data_management_error(self):
        """Test DataManagementError."""
        error = DataManagementError("Data management operation failed")
        assert str(error) == "Data management operation failed"
        assert isinstance(error, MilvusClientError)

    def test_advanced_operation_error(self):
        """Test AdvancedOperationError."""
        error = AdvancedOperationError("Advanced operation failed")
        assert str(error) == "Advanced operation failed"
        assert isinstance(error, MilvusClientError)

    def test_dev_tools_error(self):
        """Test DevToolsError."""
        error = DevToolsError("Dev tools operation failed")
        assert str(error) == "Dev tools operation failed"
        assert isinstance(error, MilvusClientError)

    def test_milvus_error(self):
        """Test MilvusError."""
        error = MilvusError("General Milvus error")
        assert str(error) == "General Milvus error"
        assert isinstance(error, MilvusClientError)

    def test_exception_inheritance(self):
        """Test exception inheritance hierarchy."""
        # All custom exceptions should inherit from MilvusClientError
        exceptions = [
            ConfigurationError,
            ConnectionError,
            CollectionError,
            InsertError,
            SearchError,
            IndexError,
            DataSourceError,
            CloudStorageError,
            APIError,
            ValidationError,
            BatchOperationError,
            StreamingError,
            SecurityError,
            MonitoringError,
            PerformanceError,
            DistributedError,
            ErrorRecoveryError,
            DataManagementError,
            AdvancedOperationError,
            DevToolsError,
            MilvusError
        ]
        
        for exc_class in exceptions:
            assert issubclass(exc_class, MilvusClientError)
            assert issubclass(exc_class, Exception)

    def test_exception_with_cause(self):
        """Test exception chaining."""
        original_error = ValueError("Original error")

        try:
            try:
                raise original_error
            except ValueError as e:
                raise ConnectionError("Connection failed") from e
        except ConnectionError as chained_error:
            assert chained_error.__cause__ is original_error

    def test_exception_args(self):
        """Test exception with multiple arguments."""
        error = ConfigurationError("Error message", "Additional info")
        assert error.args == ("Error message", "Additional info")

    def test_exception_repr(self):
        """Test exception representation."""
        error = ValidationError("Validation failed")
        repr_str = repr(error)
        assert "ValidationError" in repr_str
        assert "Validation failed" in repr_str

    def test_exception_raising(self):
        """Test raising and catching exceptions."""
        with pytest.raises(ConnectionError) as exc_info:
            raise ConnectionError("Test connection error")
        
        assert str(exc_info.value) == "Test connection error"
        assert isinstance(exc_info.value, MilvusClientError)

    def test_exception_context_manager(self):
        """Test exception handling in context managers."""
        class TestContextManager:
            def __enter__(self):
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type is ValueError:
                    raise CollectionError("Collection error") from exc_val
                return False
        
        with pytest.raises(CollectionError):
            with TestContextManager():
                raise ValueError("Original error")

    def test_custom_exception_attributes(self):
        """Test custom exception with additional attributes."""
        class CustomError(MilvusClientError):
            def __init__(self, message, error_code=None):
                super().__init__(message)
                self.error_code = error_code
        
        error = CustomError("Custom error", error_code=500)
        assert str(error) == "Custom error"
        assert error.error_code == 500
        assert isinstance(error, MilvusClientError)
