"""
AI Prishtina VectorDB - Enterprise-grade vector database library for AI applications.

A comprehensive, production-ready Python library for building sophisticated vector database
applications. Built on top of ChromaDB, it provides enterprise-grade features for semantic
search, document processing, and AI-powered data management.
"""

__version__ = "1.0.1"
__author__ = "Alban Maxhuni, PhD"
__email__ = "info@albanmaxhuni.com"
__license__ = "AGPL-3.0-or-later OR Commercial"
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
AdvancedMetricsCollector = None

try:
    from .logger import AIPrishtinaLogger
except ImportError:
    pass

try:
    from .metrics import MetricsCollector, PerformanceMonitor, AdvancedMetricsCollector
except ImportError:
    pass

# Version 0.2.0 Features
MultiModalSearchEngine = None
CacheManager = None
PerformanceManager = None

try:
    from .multimodal_search import MultiModalSearchEngine, SearchQuery, ModalityType
except ImportError:
    pass

try:
    from .caching import CacheManager, CacheConfig
except ImportError:
    pass

try:
    from .performance import PerformanceManager, PerformanceConfig
except ImportError:
    pass

# Version 0.3.0 Features
ClusterManager = None
AdvancedQueryLanguage = None
CollaborationManager = None
SecurityManager = None

try:
    from .distributed import ClusterManager, DistributedConfig
except ImportError:
    pass

try:
    from .query_language import AdvancedQueryLanguage, QueryParser
except ImportError:
    pass

try:
    from .collaboration import CollaborationManager, User as CollabUser
except ImportError:
    pass

try:
    from .security import SecurityManager, SecurityConfig
except ImportError:
    pass

# Version 1.0.0 Features
EnterpriseManager = None
AnalyticsManager = None
TenantManager = None

try:
    from .enterprise import EnterpriseManager, EnterpriseConfig
except ImportError:
    pass

try:
    from .analytics import AnalyticsManager, ReportGenerator
except ImportError:
    pass

try:
    from .multitenancy import TenantManager, Tenant
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
if AdvancedMetricsCollector is not None:
    __all__.append("AdvancedMetricsCollector")

# Add Version 0.2.0 features to __all__
if MultiModalSearchEngine is not None:
    __all__.extend(["MultiModalSearchEngine", "SearchQuery", "ModalityType"])
if CacheManager is not None:
    __all__.extend(["CacheManager", "CacheConfig"])
if PerformanceManager is not None:
    __all__.extend(["PerformanceManager", "PerformanceConfig"])

# Add Version 0.3.0 features to __all__
if ClusterManager is not None:
    __all__.extend(["ClusterManager", "DistributedConfig"])
if AdvancedQueryLanguage is not None:
    __all__.extend(["AdvancedQueryLanguage", "QueryParser"])
if CollaborationManager is not None:
    __all__.extend(["CollaborationManager", "CollabUser"])
if SecurityManager is not None:
    __all__.extend(["SecurityManager", "SecurityConfig"])

# Add Version 1.0.0 features to __all__
if EnterpriseManager is not None:
    __all__.extend(["EnterpriseManager", "EnterpriseConfig"])
if AnalyticsManager is not None:
    __all__.extend(["AnalyticsManager", "ReportGenerator"])
if TenantManager is not None:
    __all__.extend(["TenantManager", "Tenant"])