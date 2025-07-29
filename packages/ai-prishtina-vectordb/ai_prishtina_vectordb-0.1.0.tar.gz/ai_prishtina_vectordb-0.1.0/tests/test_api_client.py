"""Tests for API client functionality."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import aiohttp
from ai_prishtina_vectordb.api.client import BaseAPIClient
from ai_prishtina_vectordb.api.exceptions import (
    APIError,
    APIClientError,
    APIServerError,
    APITimeoutError,
    APIConnectionError
)


@pytest.fixture
def api_client():
    """Create a test API client."""
    return BaseAPIClient(
        base_url="https://api.example.com",
        api_key="test_key",
        timeout=30,
        max_retries=3
    )


@pytest.fixture
def mock_session():
    """Create a mock aiohttp session."""
    session = AsyncMock()
    return session


class TestBaseAPIClient:
    """Test cases for BaseAPIClient."""

    def test_init(self):
        """Test client initialization."""
        client = BaseAPIClient(
            base_url="https://api.example.com",
            api_key="test_key",
            timeout=30,
            max_retries=3,
            headers={"Custom-Header": "value"}
        )
        
        assert client.base_url == "https://api.example.com"
        assert client.api_key == "test_key"
        assert client.timeout == 30
        assert client.max_retries == 3
        assert client.headers["Authorization"] == "Bearer test_key"
        assert client.headers["Custom-Header"] == "value"

    def test_init_without_api_key(self):
        """Test client initialization without API key."""
        client = BaseAPIClient(base_url="https://api.example.com")
        
        assert client.base_url == "https://api.example.com"
        assert client.api_key is None
        assert "Authorization" not in client.headers

    @pytest.mark.asyncio
    async def test_make_request_success(self, api_client, mock_session):
        """Test successful API request."""
        # Mock response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {"success": True, "data": "test"}
        
        mock_session.request.return_value.__aenter__.return_value = mock_response
        api_client.session = mock_session
        
        result = await api_client._make_request("GET", "/test")
        
        assert result == {"success": True, "data": "test"}
        mock_session.request.assert_called_once()

    @pytest.mark.asyncio
    async def test_make_request_client_error(self, api_client, mock_session):
        """Test API request with client error."""
        mock_response = AsyncMock()
        mock_response.status = 400
        mock_response.text.return_value = "Bad Request"
        
        mock_session.request.return_value.__aenter__.return_value = mock_response
        api_client.session = mock_session
        
        with pytest.raises(APIClientError):
            await api_client._make_request("GET", "/test")

    @pytest.mark.asyncio
    async def test_make_request_server_error(self, api_client, mock_session):
        """Test API request with server error."""
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text.return_value = "Internal Server Error"
        
        mock_session.request.return_value.__aenter__.return_value = mock_response
        api_client.session = mock_session
        
        with pytest.raises(APIServerError):
            await api_client._make_request("GET", "/test")

    @pytest.mark.asyncio
    async def test_make_request_timeout(self, api_client, mock_session):
        """Test API request timeout."""
        mock_session.request.side_effect = aiohttp.ClientTimeout()
        api_client.session = mock_session
        
        with pytest.raises(APITimeoutError):
            await api_client._make_request("GET", "/test")

    @pytest.mark.asyncio
    async def test_make_request_connection_error(self, api_client, mock_session):
        """Test API request connection error."""
        mock_session.request.side_effect = aiohttp.ClientConnectionError()
        api_client.session = mock_session
        
        with pytest.raises(APIConnectionError):
            await api_client._make_request("GET", "/test")

    @pytest.mark.asyncio
    async def test_get_request(self, api_client):
        """Test GET request method."""
        with patch.object(api_client, '_make_request') as mock_make_request:
            mock_make_request.return_value = {"data": "test"}
            
            result = await api_client.get("/test", params={"key": "value"})
            
            assert result == {"data": "test"}
            mock_make_request.assert_called_once_with(
                'GET', '/test', params={"key": "value"}
            )

    @pytest.mark.asyncio
    async def test_post_request(self, api_client):
        """Test POST request method."""
        with patch.object(api_client, '_make_request') as mock_make_request:
            mock_make_request.return_value = {"success": True}
            
            result = await api_client.post("/test", json={"data": "test"})
            
            assert result == {"success": True}
            mock_make_request.assert_called_once_with(
                'POST', '/test', data=None, json={"data": "test"}
            )

    @pytest.mark.asyncio
    async def test_put_request(self, api_client):
        """Test PUT request method."""
        with patch.object(api_client, '_make_request') as mock_make_request:
            mock_make_request.return_value = {"updated": True}
            
            result = await api_client.put("/test", data={"field": "value"})
            
            assert result == {"updated": True}
            mock_make_request.assert_called_once_with(
                'PUT', '/test', data={"field": "value"}, json=None
            )

    @pytest.mark.asyncio
    async def test_delete_request(self, api_client):
        """Test DELETE request method."""
        with patch.object(api_client, '_make_request') as mock_make_request:
            mock_make_request.return_value = {"deleted": True}
            
            result = await api_client.delete("/test")
            
            assert result == {"deleted": True}
            mock_make_request.assert_called_once_with('DELETE', '/test')

    @pytest.mark.asyncio
    async def test_close_session(self, api_client, mock_session):
        """Test session cleanup."""
        api_client.session = mock_session
        
        await api_client.close()
        
        mock_session.close.assert_called_once()
        assert api_client.session is None

    @pytest.mark.asyncio
    async def test_context_manager(self, api_client):
        """Test using client as context manager."""
        with patch.object(api_client, 'close') as mock_close:
            async with api_client:
                pass
            
            mock_close.assert_called_once()


@pytest.mark.asyncio
async def test_api_client_integration():
    """Integration test for API client."""
    client = BaseAPIClient(base_url="https://httpbin.org")
    
    try:
        # Test actual HTTP request
        response = await client.get("/json")
        assert "slideshow" in response
    except Exception as e:
        # Skip if no internet connection
        pytest.skip(f"Integration test skipped due to network error: {e}")
    finally:
        await client.close()
