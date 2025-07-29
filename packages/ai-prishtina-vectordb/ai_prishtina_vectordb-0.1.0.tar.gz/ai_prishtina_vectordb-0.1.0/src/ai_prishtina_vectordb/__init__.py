"""
AI Prishtina VectorDB - Enterprise-grade vector database library for AI applications.

A comprehensive, production-ready Python library for building sophisticated vector database
applications. Built on top of ChromaDB, it provides enterprise-grade features for semantic
search, document processing, and AI-powered data management.
"""

__version__ = "0.1.0"
__author__ = "Alban Maxhuni, PhD"
__email__ = "info@albanmaxhuni.com"
__license__ = "MIT"
__title__ = "ai-prishtina-vectordb"
__description__ = "Enterprise-grade vector database library for AI applications"
__url__ = "https://github.com/albanmaxhuni/ai-prishtina-chromadb-client"

# Base exception that's always available
class AIPrishtinaError(Exception):
    """Base exception for AI Prishtina VectorDB."""
    pass

# Core components - import with error handling
Database = None
DataSource = None
EmbeddingModel = None
Vectorizer = None

try:
    from .database import Database
except ImportError:
    pass

try:
    from .data_sources import DataSource
except ImportError:
    pass

try:
    from .embeddings import EmbeddingModel
except ImportError:
    pass

try:
    from .vectorizer import Vectorizer
except ImportError:
    pass

# Configuration components
Config = None
DatabaseConfig = None
CacheConfig = None
LoggingConfig = None

try:
    from .config import Config, DatabaseConfig, CacheConfig, LoggingConfig
except ImportError:
    pass

# Utility components
AIPrishtinaLogger = None
MetricsCollector = None
PerformanceMonitor = None

try:
    from .logger import AIPrishtinaLogger
except ImportError:
    pass

try:
    from .metrics import MetricsCollector, PerformanceMonitor
except ImportError:
    pass

# Define what gets exported
__all__ = ["AIPrishtinaError"]

# Add available components to __all__
if Database is not None:
    __all__.append("Database")
if DataSource is not None:
    __all__.append("DataSource")
if EmbeddingModel is not None:
    __all__.append("EmbeddingModel")
if Vectorizer is not None:
    __all__.append("Vectorizer")
if Config is not None:
    __all__.extend(["Config", "DatabaseConfig", "CacheConfig", "LoggingConfig"])
if AIPrishtinaLogger is not None:
    __all__.append("AIPrishtinaLogger")
if MetricsCollector is not None:
    __all__.extend(["MetricsCollector", "PerformanceMonitor"])