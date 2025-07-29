"""
Docker manager for AIPrishtina VectorDB.
"""

import os
import docker
from typing import Dict, Any, Optional
import logging
from .config_manager import ConfigManager
from ..exceptions import ConfigurationError

class DockerManager:
    """Manages Docker containers for AIPrishtina VectorDB."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the Docker manager.
        
        Args:
            config: Docker configuration settings
        """
        self.config = config
        self.client = docker.from_env()
        self.logger = logging.getLogger(__name__)
    
    def start_chroma_container(self) -> bool:
        """
        Start the ChromaDB container.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            settings = self.config['docker_settings']
            
            # Check if container already exists
            try:
                container = self.client.containers.get(settings['container_name'])
                if container.status == 'running':
                    self.logger.info(f"Container {settings['container_name']} is already running")
                    return True
                container.start()
                return True
            except docker.errors.NotFound:
                pass
            
            # Create and start new container
            container = self.client.containers.run(
                image=settings['image'],
                name=settings['container_name'],
                detach=True,
                restart_policy={"Name": settings['restart_policy']},
                mem_limit=settings['memory_limit'],
                cpu_period=100000,
                cpu_quota=int(settings['cpu_limit']) * 100000,
                ports={f"{settings['exposed_port']}/tcp": settings['exposed_port']},
                volumes={
                    settings['data_volume']: {'bind': '/data', 'mode': 'rw'},
                    settings['config_volume']: {'bind': '/config', 'mode': 'rw'}
                },
                network=settings['network_name']
            )
            
            self.logger.info(f"Started ChromaDB container: {container.id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start ChromaDB container: {str(e)}")
            return False
    
    def stop_chroma_container(self) -> bool:
        """
        Stop the ChromaDB container.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            settings = self.config['docker_settings']
            container = self.client.containers.get(settings['container_name'])
            container.stop()
            self.logger.info(f"Stopped ChromaDB container: {container.id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to stop ChromaDB container: {str(e)}")
            return False
    
    def create_volumes(self) -> bool:
        """
        Create Docker volumes for ChromaDB.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            settings = self.config['docker_settings']
            
            # Create data volume
            self.client.volumes.create(
                name=settings['data_volume'],
                driver='local'
            )
            
            # Create config volume
            self.client.volumes.create(
                name=settings['config_volume'],
                driver='local'
            )
            
            self.logger.info("Created Docker volumes for ChromaDB")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create Docker volumes: {str(e)}")
            return False
    
    def create_network(self) -> bool:
        """
        Create Docker network for ChromaDB.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            settings = self.config['docker_settings']
            
            # Create network if it doesn't exist
            try:
                self.client.networks.get(settings['network_name'])
            except docker.errors.NotFound:
                self.client.networks.create(
                    name=settings['network_name'],
                    driver='bridge'
                )
            
            self.logger.info(f"Created Docker network: {settings['network_name']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create Docker network: {str(e)}")
            return False
    
    def get_container_status(self) -> Dict[str, Any]:
        """
        Get the status of the ChromaDB container.
        
        Returns:
            Dict[str, Any]: Container status information
        """
        try:
            settings = self.config['docker_settings']
            container = self.client.containers.get(settings['container_name'])
            
            return {
                'id': container.id,
                'status': container.status,
                'name': container.name,
                'image': container.image.tags[0] if container.image.tags else container.image.id,
                'ports': container.ports,
                'created': container.attrs['Created'],
                'state': container.attrs['State']
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get container status: {str(e)}")
            return {
                'error': str(e),
                'status': 'not_found'
            }
    
    def setup_chroma_environment(self) -> bool:
        """
        Set up the complete ChromaDB environment.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create volumes
            if not self.create_volumes():
                return False
            
            # Create network
            if not self.create_network():
                return False
            
            # Start container
            if not self.start_chroma_container():
                return False
            
            self.logger.info("Successfully set up ChromaDB environment")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set up ChromaDB environment: {str(e)}")
            return False 