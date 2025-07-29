"""
Custom exceptions for the Milvus client.

Copyright (c) 2025 Alban Maxhuni <alban.q.maxhuni@gmail.com>

This software is dual-licensed under AGPL-3.0 (open-source) and Commercial licenses.
For commercial licensing, contact: alban.q.maxhuni@gmail.com
"""

class MilvusClientError(Exception):
    """Base exception for all Milvus client errors."""
    pass


class ConfigurationError(MilvusClientError):
    """Raised when there is an error in the configuration."""
    pass


class ConnectionError(MilvusClientError):
    """Raised when there is an error connecting to Milvus."""
    pass


class CollectionError(MilvusClientError):
    """Raised when there is an error with collection operations."""
    pass


class InsertError(MilvusClientError):
    """Raised when there is an error inserting data."""
    pass


class SearchError(MilvusClientError):
    """Raised when there is an error searching data."""
    pass


class IndexError(MilvusClientError):
    """Raised when there is an error with index operations."""
    pass


class DataSourceError(MilvusClientError):
    """Raised when there is an error with data source operations."""
    pass


class CloudStorageError(MilvusClientError):
    """Raised when there is an error with cloud storage operations."""
    pass


class APIError(MilvusClientError):
    """Raised when there is an error with API operations."""
    pass


class ValidationError(MilvusClientError):
    """Raised when there is an error validating data."""
    pass


class BatchOperationError(MilvusClientError):
    """Raised when there is an error with batch operations."""
    pass


class StreamingError(MilvusClientError):
    """Raised when there is an error with streaming operations."""
    pass


class SecurityError(MilvusClientError):
    """Raised when there is an error with security operations."""
    pass


class MonitoringError(MilvusClientError):
    """Raised when there is an error with monitoring operations."""
    pass


class PerformanceError(MilvusClientError):
    """Raised when there is an error with performance operations."""
    pass


class DistributedError(MilvusClientError):
    """Raised when there is an error with distributed operations."""
    pass


class ErrorRecoveryError(MilvusClientError):
    """Raised when there is an error with error recovery operations."""
    pass


class DataManagementError(MilvusClientError):
    """Raised when there is an error with data management operations."""
    pass


class AdvancedOperationError(MilvusClientError):
    """Raised when there is an error with advanced operations."""
    pass


class DevToolsError(MilvusClientError):
    """Raised when there is an error with development tools."""
    pass


class IntegrationError(MilvusClientError):
    """Raised when there is an error with integration operations."""
    pass


class MilvusError(MilvusClientError):
    """General Milvus error."""
    pass