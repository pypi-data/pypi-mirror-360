"""
Configuration manager for AIPrishtina VectorDB.
"""

import os
import configparser
import yaml
import json
from typing import Dict, Any, Optional, Union
from pathlib import Path
import logging
from ..exceptions import ConfigurationError

class ConfigManager:
    """Manages configuration settings for AIPrishtina VectorDB."""
    
    def __init__(self, config_path: Optional[str] = None, config_type: str = "yaml"):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration file. Required for Docker mode.
            config_type: Type of configuration file ("yaml" or "ini"). Defaults to "yaml".
            
        Raises:
            ValueError: If config_path is not provided in Docker mode
            FileNotFoundError: If config file is not found
        """
        self.config_type = config_type.lower()
        self.logger = logging.getLogger(__name__)
        
        # Check if we're in Docker mode
        is_docker_mode = os.getenv('AI_PRISHTINA_DOCKER_MODE', 'false').lower() == 'true'
        
        if is_docker_mode and not config_path:
            raise ValueError(
                "Configuration file path is required in Docker mode. "
                "Please provide a path to either a .yaml or .ini configuration file."
            )
        
        if config_path is None:
            # Use default config path
            default_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'config',
                f'config.{self.config_type}'
            )
            config_path = os.getenv('AI_PRISHTINA_CONFIG', default_path)
        
        self.config_path = config_path
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}. "
                "Please provide a valid configuration file."
            )
        
        if self.config_type == "yaml":
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        else:
            self.config = configparser.ConfigParser()
            self.config.read(self.config_path)
    
    def _get_value(self, section: str, key: str, default: Any = None) -> Any:
        """Get a configuration value, handling both YAML and INI formats."""
        try:
            if self.config_type == "yaml":
                return self.config[section][key]
            else:
                return self.config.get(section, key)
        except (KeyError, configparser.NoOptionError):
            if default is not None:
                return default
            raise
    
    def get_chroma_settings(self) -> Dict[str, Any]:
        """Get ChromaDB settings."""
        section = "chromadb"
        return {
            'host': self._get_value(section, 'host'),
            'port': int(self._get_value(section, 'port')),
            'ssl': self._get_value(section, 'ssl', 'false').lower() == 'true',
            'api_key': self._get_value(section, 'api_key'),
            'collection_name': self._get_value(section, 'collection_name'),
            'persist_directory': self._get_value(section, 'persist_directory'),
            'allow_reset': self._get_value(section, 'allow_reset', 'true').lower() == 'true',
            'anonymized_telemetry': self._get_value(section, 'anonymized_telemetry', 'false').lower() == 'true',
            'embedding_function': self._get_value(section, 'embedding_function'),
            'default_embedding_model': self._get_value(section, 'default_embedding_model'),
            'embedding_dimension': int(self._get_value(section, 'embedding_dimension')),
            'batch_size': int(self._get_value(section, 'batch_size')),
            'cache_size': int(self._get_value(section, 'cache_size')),
            'max_retries': int(self._get_value(section, 'max_retries')),
            'timeout': int(self._get_value(section, 'timeout'))
        }
    
    def get_docker_settings(self) -> Dict[str, Any]:
        """Get Docker settings."""
        section = "docker"
        return {
            'container_name': self._get_value(section, 'container_name'),
            'image': self._get_value(section, 'image'),
            'restart_policy': self._get_value(section, 'restart_policy'),
            'memory_limit': self._get_value(section, 'memory_limit'),
            'cpu_limit': int(self._get_value(section, 'cpu_limit')),
            'data_volume': self._get_value(section, 'data_volume'),
            'config_volume': self._get_value(section, 'config_volume'),
            'network_name': self._get_value(section, 'network_name'),
            'exposed_port': int(self._get_value(section, 'exposed_port'))
        }
    
    def get_security_settings(self) -> Dict[str, Any]:
        """Get security settings."""
        section = "security"
        return {
            'auth_enabled': self._get_value(section, 'auth_enabled', 'false').lower() == 'true',
            'auth_credentials_file': self._get_value(section, 'auth_credentials_file'),
            'jwt_secret': self._get_value(section, 'jwt_secret'),
            'token_expiry': int(self._get_value(section, 'token_expiry')),
            'ssl_enabled': self._get_value(section, 'ssl_enabled', 'false').lower() == 'true',
            'ssl_cert_file': self._get_value(section, 'ssl_cert_file'),
            'ssl_key_file': self._get_value(section, 'ssl_key_file')
        }
    
    def get_logging_settings(self) -> Dict[str, Any]:
        """Get logging settings."""
        section = "logging"
        return {
            'level': self._get_value(section, 'level'),
            'format': self._get_value(section, 'format'),
            'file': self._get_value(section, 'file'),
            'max_size': self._get_value(section, 'max_size'),
            'backup_count': int(self._get_value(section, 'backup_count'))
        }
    
    def get_monitoring_settings(self) -> Dict[str, Any]:
        """Get monitoring settings."""
        section = "monitoring"
        return {
            'metrics_enabled': self._get_value(section, 'metrics_enabled', 'true').lower() == 'true',
            'prometheus_port': int(self._get_value(section, 'prometheus_port')),
            'health_check_interval': int(self._get_value(section, 'health_check_interval')),
            'alert_threshold': float(self._get_value(section, 'alert_threshold'))
        }
    
    def update_setting(self, section: str, option: str, value: Any):
        """
        Update a configuration setting.
        
        Args:
            section: Configuration section
            option: Configuration option
            value: New value
        """
        if self.config_type == "yaml":
            if section not in self.config:
                self.config[section] = {}
            self.config[section][option] = value
        else:
            if not self.config.has_section(section):
                self.config.add_section(section)
            self.config.set(section, option, str(value))
        
        # Save changes to file
        with open(self.config_path, 'w') as f:
            if self.config_type == "yaml":
                yaml.dump(self.config, f, default_flow_style=False)
            else:
                self.config.write(f)
    
    def get_all_settings(self) -> Dict[str, Dict[str, Any]]:
        """Get all configuration settings."""
        return {
            'chromadb': self.get_chroma_settings(),
            'docker': self.get_docker_settings(),
            'security': self.get_security_settings(),
            'logging': self.get_logging_settings(),
            'monitoring': self.get_monitoring_settings()
        }
    
    def validate_config(self) -> bool:
        """
        Validate the configuration settings.
        
        Returns:
            bool: True if configuration is valid, False otherwise
        """
        try:
            # Check required sections
            required_sections = ['chromadb', 'docker', 'security', 'logging', 'monitoring']
            for section in required_sections:
                if self.config_type == "yaml":
                    if section not in self.config:
                        self.logger.error(f"Missing required section: {section}")
                        return False
                else:
                    if not self.config.has_section(section):
                        self.logger.error(f"Missing required section: {section}")
                        return False
            
            # Validate specific settings
            self.get_chroma_settings()
            self.get_docker_settings()
            self.get_security_settings()
            self.get_logging_settings()
            self.get_monitoring_settings()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {str(e)}")
            return False 