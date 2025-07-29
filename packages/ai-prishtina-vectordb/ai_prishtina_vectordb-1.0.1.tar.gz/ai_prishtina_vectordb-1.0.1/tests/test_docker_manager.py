"""Tests for Docker manager functionality."""

import pytest
from unittest.mock import MagicMock, patch, Mock
import docker
from ai_prishtina_vectordb.config.docker_manager import DockerManager
from ai_prishtina_vectordb.config.config_manager import ConfigManager


@pytest.fixture
def mock_config():
    """Create a mock configuration."""
    config = {
        'docker_settings': {
            'image': 'chromadb/chroma:latest',
            'container_name': 'test_chroma',
            'exposed_port': 8000,
            'restart_policy': 'unless-stopped',
            'memory_limit': '1g',
            'cpu_limit': 1.0,
            'data_volume': '/tmp/chroma_data',
            'config_volume': '/tmp/chroma_config',
            'network_name': 'chroma_network'
        }
    }
    return config


@pytest.fixture
def mock_config_manager(mock_config):
    """Create a mock config manager."""
    config_manager = MagicMock(spec=ConfigManager)
    config_manager.config = mock_config
    config_manager.__getitem__ = lambda self, key: mock_config[key]
    return config_manager


@pytest.fixture
def mock_docker_client():
    """Create a mock Docker client."""
    client = MagicMock(spec=docker.DockerClient)
    return client


@pytest.fixture
def docker_manager(mock_config_manager):
    """Create a Docker manager instance."""
    with patch('ai_prishtina_vectordb.config.docker_manager.docker.from_env') as mock_docker:
        mock_client = MagicMock()
        mock_docker.return_value = mock_client
        manager = DockerManager(mock_config_manager)
        manager.client = mock_client
        return manager


class TestDockerManager:
    """Test cases for DockerManager."""

    def test_init(self, mock_config_manager):
        """Test Docker manager initialization."""
        with patch('ai_prishtina_vectordb.config.docker_manager.docker.from_env') as mock_docker:
            mock_client = MagicMock()
            mock_docker.return_value = mock_client
            
            manager = DockerManager(mock_config_manager)
            
            assert manager.config_manager == mock_config_manager
            assert manager.config == mock_config_manager.config
            mock_docker.assert_called_once()

    def test_init_docker_not_available(self, mock_config_manager):
        """Test initialization when Docker is not available."""
        with patch('ai_prishtina_vectordb.config.docker_manager.docker.from_env') as mock_docker:
            mock_docker.side_effect = docker.errors.DockerException("Docker not available")
            
            with pytest.raises(docker.errors.DockerException):
                DockerManager(mock_config_manager)

    def test_start_chroma_container_new(self, docker_manager):
        """Test starting a new ChromaDB container."""
        # Mock container not found, then create new one
        mock_container = MagicMock()
        docker_manager.client.containers.get.side_effect = docker.errors.NotFound("Container not found")
        docker_manager.client.containers.run.return_value = mock_container
        
        result = docker_manager.start_chroma_container()
        
        assert result is True
        docker_manager.client.containers.run.assert_called_once()

    def test_start_chroma_container_existing_running(self, docker_manager):
        """Test starting an existing running container."""
        mock_container = MagicMock()
        mock_container.status = 'running'
        docker_manager.client.containers.get.return_value = mock_container
        
        result = docker_manager.start_chroma_container()
        
        assert result is True
        docker_manager.client.containers.get.assert_called_once()
        mock_container.start.assert_not_called()

    def test_start_chroma_container_existing_stopped(self, docker_manager):
        """Test starting an existing stopped container."""
        mock_container = MagicMock()
        mock_container.status = 'stopped'
        docker_manager.client.containers.get.return_value = mock_container
        
        result = docker_manager.start_chroma_container()
        
        assert result is True
        mock_container.start.assert_called_once()

    def test_start_chroma_container_error(self, docker_manager):
        """Test error handling when starting container fails."""
        docker_manager.client.containers.get.side_effect = docker.errors.NotFound("Container not found")
        docker_manager.client.containers.run.side_effect = docker.errors.APIError("API Error")
        
        result = docker_manager.start_chroma_container()
        
        assert result is False

    def test_stop_chroma_container_success(self, docker_manager):
        """Test stopping ChromaDB container successfully."""
        mock_container = MagicMock()
        docker_manager.client.containers.get.return_value = mock_container
        
        result = docker_manager.stop_chroma_container()
        
        assert result is True
        mock_container.stop.assert_called_once()

    def test_stop_chroma_container_not_found(self, docker_manager):
        """Test stopping container when it doesn't exist."""
        docker_manager.client.containers.get.side_effect = docker.errors.NotFound("Container not found")
        
        result = docker_manager.stop_chroma_container()
        
        assert result is False

    def test_remove_chroma_container_success(self, docker_manager):
        """Test removing ChromaDB container successfully."""
        mock_container = MagicMock()
        docker_manager.client.containers.get.return_value = mock_container
        
        result = docker_manager.remove_chroma_container()
        
        assert result is True
        mock_container.remove.assert_called_once_with(force=True)

    def test_remove_chroma_container_not_found(self, docker_manager):
        """Test removing container when it doesn't exist."""
        docker_manager.client.containers.get.side_effect = docker.errors.NotFound("Container not found")
        
        result = docker_manager.remove_chroma_container()
        
        assert result is False

    def test_create_volumes_success(self, docker_manager):
        """Test creating Docker volumes successfully."""
        docker_manager.client.volumes.get.side_effect = docker.errors.NotFound("Volume not found")
        mock_volume = MagicMock()
        docker_manager.client.volumes.create.return_value = mock_volume
        
        result = docker_manager.create_volumes()
        
        assert result is True
        assert docker_manager.client.volumes.create.call_count == 2

    def test_create_volumes_existing(self, docker_manager):
        """Test creating volumes when they already exist."""
        mock_volume = MagicMock()
        docker_manager.client.volumes.get.return_value = mock_volume
        
        result = docker_manager.create_volumes()
        
        assert result is True
        docker_manager.client.volumes.create.assert_not_called()

    def test_create_network_success(self, docker_manager):
        """Test creating Docker network successfully."""
        docker_manager.client.networks.get.side_effect = docker.errors.NotFound("Network not found")
        mock_network = MagicMock()
        docker_manager.client.networks.create.return_value = mock_network
        
        result = docker_manager.create_network()
        
        assert result is True
        docker_manager.client.networks.create.assert_called_once()

    def test_create_network_existing(self, docker_manager):
        """Test creating network when it already exists."""
        mock_network = MagicMock()
        docker_manager.client.networks.get.return_value = mock_network
        
        result = docker_manager.create_network()
        
        assert result is True
        docker_manager.client.networks.create.assert_not_called()

    def test_get_container_status_running(self, docker_manager):
        """Test getting status of running container."""
        mock_container = MagicMock()
        mock_container.status = 'running'
        mock_container.attrs = {
            'State': {'Status': 'running'},
            'NetworkSettings': {'Ports': {'8000/tcp': [{'HostPort': '8000'}]}}
        }
        docker_manager.client.containers.get.return_value = mock_container
        
        status = docker_manager.get_container_status()
        
        assert status['status'] == 'running'
        assert status['exists'] is True

    def test_get_container_status_not_found(self, docker_manager):
        """Test getting status when container doesn't exist."""
        docker_manager.client.containers.get.side_effect = docker.errors.NotFound("Container not found")
        
        status = docker_manager.get_container_status()
        
        assert status['status'] == 'not_found'
        assert status['exists'] is False

    def test_setup_chroma_environment_success(self, docker_manager):
        """Test setting up complete ChromaDB environment."""
        with patch.object(docker_manager, 'create_volumes', return_value=True), \
             patch.object(docker_manager, 'create_network', return_value=True), \
             patch.object(docker_manager, 'start_chroma_container', return_value=True):
            
            result = docker_manager.setup_chroma_environment()
            
            assert result is True

    def test_setup_chroma_environment_failure(self, docker_manager):
        """Test setup failure when volumes creation fails."""
        with patch.object(docker_manager, 'create_volumes', return_value=False):
            
            result = docker_manager.setup_chroma_environment()
            
            assert result is False

    def test_cleanup_chroma_environment_success(self, docker_manager):
        """Test cleaning up ChromaDB environment."""
        with patch.object(docker_manager, 'stop_chroma_container', return_value=True), \
             patch.object(docker_manager, 'remove_chroma_container', return_value=True):
            
            result = docker_manager.cleanup_chroma_environment()
            
            assert result is True

    def test_cleanup_chroma_environment_partial_failure(self, docker_manager):
        """Test cleanup with partial failure."""
        with patch.object(docker_manager, 'stop_chroma_container', return_value=True), \
             patch.object(docker_manager, 'remove_chroma_container', return_value=False):
            
            result = docker_manager.cleanup_chroma_environment()
            
            assert result is False
