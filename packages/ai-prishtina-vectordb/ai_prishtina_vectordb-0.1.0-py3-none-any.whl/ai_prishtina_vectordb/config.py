"""
Configuration management for the AIPrishtina VectorDB library.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import os
import json
from pathlib import Path
import aiofiles
from .logger import AIPrishtinaLogger

@dataclass
class DatabaseConfig:
    """Configuration for database settings."""
    collection_name: str = "ai_prishtina_collection"
    persist_directory: str = field(default_factory=lambda: os.path.join(os.getcwd(), ".chroma"))
    embedding_model: Optional[str] = None
    index_type: str = "hnsw"
    index_params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CacheConfig:
    """Configuration for caching settings."""
    enabled: bool = True
    cache_type: str = "memory"  # memory, redis, file
    cache_dir: str = field(default_factory=lambda: os.path.join(os.getcwd(), ".cache"))
    max_size: int = 1000
    ttl: int = 3600  # Time to live in seconds
    redis_url: Optional[str] = None

@dataclass
class LoggingConfig:
    """Configuration for logging settings."""
    level: str = "INFO"
    log_file: str = field(default_factory=lambda: os.path.join(os.getcwd(), "logs", "ai_prishtina.log"))
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    max_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5

@dataclass
class Config:
    """Main configuration class for AIPrishtina VectorDB."""
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    def __init__(
        self,
        database: Optional[DatabaseConfig] = None,
        logging: Optional[LoggingConfig] = None,
        cache: Optional[CacheConfig] = None
    ):
        """Initialize configuration.

        Args:
            database: Database configuration
            logging: Logging configuration
            cache: Cache configuration
        """
        self.database = database or DatabaseConfig()
        self.logging = logging or LoggingConfig()
        self.cache = cache or CacheConfig()

    def create_directories(self):
        """Create necessary directories for the application."""
        # Create database directory
        if self.database.persist_directory:
            os.makedirs(self.database.persist_directory, exist_ok=True)

        # Create cache directory
        if self.cache.cache_dir:
            os.makedirs(self.cache.cache_dir, exist_ok=True)

        # Create log directory
        if self.logging.log_file:
            log_dir = os.path.dirname(self.logging.log_file)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)

class DatabaseConfigManager:
    """Configuration manager for AIPrishtina VectorDB."""
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        logger: Optional[AIPrishtinaLogger] = None
    ):
        """Initialize configuration manager.
        
        Args:
            config_path: Path to configuration file
            logger: Optional logger instance
        """
        self.logger = logger or AIPrishtinaLogger()
        self.config_path = config_path or os.path.join(
            os.path.expanduser("~"),
            ".ai_prishtina",
            "config.json"
        )
        self.config: Dict[str, Any] = {}
        
    async def load(self) -> Dict[str, Any]:
        """Load configuration from file.
        
        Returns:
            Configuration dictionary
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file is invalid
        """
        try:
            if not os.path.exists(self.config_path):
                await self.logger.warning(f"Config file not found: {self.config_path}")
                return {}
                
            async with aiofiles.open(self.config_path, 'r') as f:
                content = await f.read()
                self.config = json.loads(content)
                await self.logger.info("Loaded configuration from file")
                return self.config
        except Exception as e:
            await self.logger.error(f"Failed to load configuration: {str(e)}")
            raise
            
    async def save(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Save configuration to file.
        
        Args:
            config: Optional configuration to save
        """
        try:
            if config is not None:
                self.config = config
                
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            async with aiofiles.open(self.config_path, 'w') as f:
                await f.write(json.dumps(self.config, indent=2))
                await self.logger.info("Saved configuration to file")
        except Exception as e:
            await self.logger.error(f"Failed to save configuration: {str(e)}")
            raise
            
    async def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
        
    async def set(self, key: str, value: Any) -> None:
        """Set configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self.config[key] = value
        await self.save()
        
    async def update(self, config: Dict[str, Any]) -> None:
        """Update configuration with new values.
        
        Args:
            config: New configuration values
        """
        self.config.update(config)
        await self.save()
        
    async def delete(self, key: str) -> None:
        """Delete configuration value.
        
        Args:
            key: Configuration key to delete
        """
        if key in self.config:
            del self.config[key]
            await self.save()
            
    async def clear(self) -> None:
        """Clear all configuration values."""
        self.config = {}
        await self.save()
        
    async def get_all(self) -> Dict[str, Any]:
        """Get all configuration values.
        
        Returns:
            Complete configuration dictionary
        """
        return self.config.copy()
        
    async def validate(self) -> bool:
        """Validate configuration.
        
        Returns:
            True if configuration is valid
        """
        required_keys = ["embedding_model", "index_type"]
        return all(key in self.config for key in required_keys)
        
    async def reset(self) -> None:
        """Reset configuration to default values."""
        self.config = {
            "embedding_model": "all-MiniLM-L6-v2",
            "index_type": "hnsw",
            "batch_size": 32,
            "normalize_embeddings": True
        }
        await self.save()
        
    async def merge(self, other_config: Dict[str, Any]) -> None:
        """Merge another configuration into current one.
        
        Args:
            other_config: Configuration to merge
        """
        self.config = {**self.config, **other_config}
        await self.save()
        
    async def export(self, path: str) -> None:
        """Export configuration to file.
        
        Args:
            path: Export file path
        """
        try:
            async with aiofiles.open(path, 'w') as f:
                await f.write(json.dumps(self.config, indent=2))
                await self.logger.info(f"Exported configuration to {path}")
        except Exception as e:
            await self.logger.error(f"Failed to export configuration: {str(e)}")
            raise
            
    async def import_config(self, path: str) -> None:
        """Import configuration from file.
        
        Args:
            path: Import file path
        """
        try:
            async with aiofiles.open(path, 'r') as f:
                content = await f.read()
                self.config = json.loads(content)
                await self.save()
                await self.logger.info(f"Imported configuration from {path}")
        except Exception as e:
            await self.logger.error(f"Failed to import configuration: {str(e)}")
            raise 