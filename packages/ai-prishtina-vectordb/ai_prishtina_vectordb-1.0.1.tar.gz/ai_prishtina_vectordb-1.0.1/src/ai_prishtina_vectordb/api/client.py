"""
Base API client for AIPrishtina VectorDB.
"""

from typing import Dict, Any, Optional, Union
import aiohttp
from .exceptions import (
    APIError,
    APIConfigurationError,
    APIAuthenticationError,
    APIRateLimitError,
    APIValidationError,
    APINotFoundError,
    APIConnectionError,
    APITimeoutError,
    APIServerError,
    APIClientError
)

class BaseAPIClient:
    """Base class for API clients."""
    
    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        headers: Optional[Dict[str, str]] = None
    ):
        """Initialize the API client.
        
        Args:
            base_url: Base URL for the API
            api_key: API key for authentication
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            headers: Additional headers to include in requests
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.headers = headers or {}
        
        if api_key:
            self.headers['Authorization'] = f'Bearer {api_key}'
        
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters
            data: Form data
            json: JSON data
            headers: Additional headers
            
        Returns:
            Response data as dictionary
            
        Raises:
            APIError: If the request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        if not self.session:
            self.session = aiohttp.ClientSession(headers=self.headers)
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                params=params,
                data=data,
                json=json,
                headers=headers,
                timeout=self.timeout
            ) as response:
                # Handle different status codes
                if response.status == 200:
                    return await response.json()
                elif response.status == 400:
                    raise APIValidationError(f"Validation error: {await response.text()}")
                elif response.status == 401:
                    raise APIAuthenticationError(f"Authentication error: {await response.text()}")
                elif response.status == 403:
                    raise APIAuthenticationError(f"Permission denied: {await response.text()}")
                elif response.status == 404:
                    raise APINotFoundError(f"Resource not found: {await response.text()}")
                elif response.status == 429:
                    raise APIRateLimitError(f"Rate limit exceeded: {await response.text()}")
                elif response.status >= 500:
                    raise APIServerError(f"Server error: {await response.text()}")
                else:
                    raise APIError(f"Unexpected error: {await response.text()}")
                
        except aiohttp.ClientTimeout:
            raise APITimeoutError("Request timed out")
        except aiohttp.ClientConnectionError:
            raise APIConnectionError("Failed to connect to the API")
        except aiohttp.ClientError as e:
            raise APIClientError(f"Request failed: {str(e)}")
    
    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a GET request.
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            Response data as dictionary
        """
        return await self._make_request('GET', endpoint, params=params)
    
    async def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a POST request.
        
        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data
            
        Returns:
            Response data as dictionary
        """
        return await self._make_request('POST', endpoint, data=data, json=json)
    
    async def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a PUT request.
        
        Args:
            endpoint: API endpoint
            data: Form data
            json: JSON data
            
        Returns:
            Response data as dictionary
        """
        return await self._make_request('PUT', endpoint, data=data, json=json)
    
    async def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make a DELETE request.
        
        Args:
            endpoint: API endpoint
            
        Returns:
            Response data as dictionary
        """
        return await self._make_request('DELETE', endpoint)
    
    async def close(self):
        """Close the session."""
        if self.session:
            await self.session.close()
            self.session = None 