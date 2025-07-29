"""
Example script for setting up ChromaDB with Docker using configuration files.
This script demonstrates how to use both YAML and INI configuration files.
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from ai_prishtina_vectordb.config.config_manager import ConfigManager
from ai_prishtina_vectordb.config.docker_manager import DockerManager

def setup_chroma_with_config(config_path: str, config_type: str = "yaml"):
    """
    Set up ChromaDB using the specified configuration file.
    
    Args:
        config_path: Path to the configuration file
        config_type: Type of configuration file ("yaml" or "ini")
    """
    print(f"\nSetting up ChromaDB with {config_type.upper()} configuration...")
    print(f"Using configuration file: {config_path}")
    
    # Initialize configuration manager
    config_manager = ConfigManager(config_path=config_path, config_type=config_type)
    
    # Validate configuration
    if not config_manager.validate_config():
        print("Configuration validation failed. Please check your configuration file.")
        return
    
    # Print current settings
    print("\nCurrent configuration settings:")
    settings = config_manager.get_all_settings()
    for section, values in settings.items():
        print(f"\n{section.upper()}:")
        for key, value in values.items():
            print(f"  {key}: {value}")
    
    # Initialize Docker manager
    docker_manager = DockerManager(config_manager)
    
    try:
        # Set up ChromaDB environment
        print("\nSetting up ChromaDB environment...")
        docker_manager.setup_chroma_environment()
        
        # Get container status
        status = docker_manager.get_container_status()
        print("\nContainer status:")
        for key, value in status.items():
            print(f"  {key}: {value}")
            
    except Exception as e:
        print(f"\nError setting up ChromaDB: {str(e)}")
        return

def main():
    """Main function to demonstrate configuration usage."""
    # Get the directory of this script
    script_dir = Path(__file__).parent
    
    # Set up with YAML configuration
    yaml_config = script_dir / "config" / "config.yaml"
    if yaml_config.exists():
        setup_chroma_with_config(str(yaml_config), "yaml")
    else:
        print(f"YAML configuration file not found: {yaml_config}")
    
    # Set up with INI configuration
    ini_config = script_dir / "config" / "config.ini"
    if ini_config.exists():
        setup_chroma_with_config(str(ini_config), "ini")
    else:
        print(f"INI configuration file not found: {ini_config}")

if __name__ == "__main__":
    main() 