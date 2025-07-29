"""
Unit tests for the configuration module.
"""

import os
import pytest
from pathlib import Path
from ai_prishtina_vectordb import Config, DatabaseConfig, CacheConfig, LoggingConfig

@pytest.fixture
def config():
    """Create a test configuration."""
    return Config()

def test_default_config(config):
    """Test default configuration values."""
    # Match new defaults
    assert config.database.persist_directory.endswith(".chroma")
    assert config.database.collection_name == "ai_prishtina_collection"
    assert config.database.embedding_model is None
    assert config.database.index_type == "hnsw"
    assert config.database.index_params == {}
    assert config.cache.enabled is True
    assert config.cache.cache_dir.endswith(".cache")
    assert config.cache.max_size == 1000
    assert config.cache.ttl == 3600
    assert config.logging.level == "INFO"
    assert config.logging.log_file.endswith("ai_prishtina.log")
    assert config.logging.format == "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    assert config.logging.max_size == 10 * 1024 * 1024
    assert config.logging.backup_count == 5

def test_create_directories(config, tmp_path):
    """Test directory creation."""
    # Set paths to temporary directory
    config.database.persist_directory = str(tmp_path / "vectordb")
    config.cache.cache_dir = str(tmp_path / "cache")
    config.logging.log_file = str(tmp_path / "logs" / "ai_prishtina.log")
    # Create directories
    config.create_directories()
    # Verify directories exist
    assert Path(config.database.persist_directory).exists()
    assert Path(config.cache.cache_dir).exists()
    assert Path(os.path.dirname(config.logging.log_file)).exists()

def test_database_config_index_params():
    """Test database configuration index parameters."""
    config = DatabaseConfig()
    assert config.index_params == {}
    # Test custom index parameters
    custom_params = {"M": 32, "ef_construction": 200, "ef_search": 100}
    config = DatabaseConfig(index_params=custom_params)
    assert config.index_params == custom_params 