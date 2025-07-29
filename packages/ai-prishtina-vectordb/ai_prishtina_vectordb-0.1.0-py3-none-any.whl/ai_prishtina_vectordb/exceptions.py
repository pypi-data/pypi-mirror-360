"""
Custom exceptions for AI Prishtina VectorDB.
"""

class AIPrishtinaError(Exception):
    """Base exception for AI Prishtina VectorDB."""
    pass

class ConfigurationError(AIPrishtinaError):
    """Raised when there is a configuration error."""
    pass

class DataSourceError(AIPrishtinaError):
    """Raised when there is an error with the data source."""
    pass

class EmbeddingError(AIPrishtinaError):
    """Raised when there is an error with embeddings."""
    pass

class DatabaseError(AIPrishtinaError):
    """Raised when there is a database error."""
    pass

class ValidationError(AIPrishtinaError):
    """Raised when validation fails."""
    pass

class CacheError(AIPrishtinaError):
    """Raised when there is a caching error."""
    pass

class IndexError(AIPrishtinaError):
    """Raised when there is an indexing error."""
    pass

class SearchError(AIPrishtinaError):
    """Raised when there is a search error."""
    pass

class BatchProcessingError(AIPrishtinaError):
    """Raised when there is a batch processing error."""
    pass

class ResourceNotFoundError(AIPrishtinaError):
    """Raised when a requested resource is not found."""
    pass

class AuthenticationError(AIPrishtinaError):
    """Raised when there is an authentication error."""
    pass

class RateLimitError(AIPrishtinaError):
    """Raised when rate limits are exceeded."""
    pass

class FeatureError(AIPrishtinaError):
    """Raised when there is a feature processing error."""
    pass

class QueryError(AIPrishtinaError):
    """Raised when there is a query error."""
    pass

class StorageError(AIPrishtinaError):
    """Raised when there is a storage error."""
    pass

class VectorizationError(AIPrishtinaError):
    """Exception raised for vectorization errors."""
    pass

class FeatureExtractionError(AIPrishtinaError):
    """Exception raised for feature extraction errors."""
    pass

class MetricsError(AIPrishtinaError):
    """Exception raised for metrics errors."""
    pass

class LoggingError(AIPrishtinaError):
    """Exception raised for logging errors."""
    pass 