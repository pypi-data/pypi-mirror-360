"""
Feature extraction API client for AIPrishtina VectorDB.
"""

from typing import Dict, Any, List, Optional, Union
import numpy as np
from .client import BaseAPIClient
from .exceptions import APIError

class FeatureExtractionClient(BaseAPIClient):
    """Client for feature extraction API endpoints."""
    
    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        headers: Optional[Dict[str, str]] = None
    ):
        """Initialize the feature extraction client.
        
        Args:
            base_url: Base URL for the API
            api_key: API key for authentication
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            headers: Additional headers to include in requests
        """
        super().__init__(base_url, api_key, timeout, max_retries, headers)
    
    async def extract_features(
        self,
        data: Union[str, Dict[str, Any]],
        feature_type: str = "text",
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Extract features from input data.
        
        Args:
            data: Input data (text or dictionary with data)
            feature_type: Type of feature extraction ("text", "image", "audio")
            config: Feature extraction configuration
            
        Returns:
            Extracted features
        """
        endpoint = f"features/extract/{feature_type}"
        payload = {
            "data": data,
            "config": config or {}
        }
        return await self.post(endpoint, json=payload)
    
    async def batch_extract_features(
        self,
        data_list: List[Union[str, Dict[str, Any]]],
        feature_type: str = "text",
        config: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Extract features from a batch of data.
        
        Args:
            data_list: List of input data
            feature_type: Type of feature extraction ("text", "image", "audio")
            config: Feature extraction configuration
            
        Returns:
            List of extracted features
        """
        endpoint = f"features/batch-extract/{feature_type}"
        payload = {
            "data_list": data_list,
            "config": config or {}
        }
        return await self.post(endpoint, json=payload)
    
    async def process_features(
        self,
        features: Dict[str, Any],
        processor_type: str = "default",
        config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process extracted features.
        
        Args:
            features: Extracted features
            processor_type: Type of feature processor
            config: Processing configuration
            
        Returns:
            Processed features
        """
        endpoint = f"features/process/{processor_type}"
        payload = {
            "features": features,
            "config": config or {}
        }
        return await self.post(endpoint, json=payload)
    
    async def add_to_collection(
        self,
        features: Dict[str, Any],
        collection_name: str,
        id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Add features to a collection.
        
        Args:
            features: Extracted features
            collection_name: Name of the collection
            id: Document ID
            metadata: Document metadata
            
        Returns:
            Operation result
        """
        endpoint = f"collections/{collection_name}/add"
        payload = {
            "features": features,
            "id": id,
            "metadata": metadata or {}
        }
        return await self.post(endpoint, json=payload)
    
    async def query_collection(
        self,
        collection_name: str,
        query_features: Dict[str, Any],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query a collection using features.
        
        Args:
            collection_name: Name of the collection
            query_features: Query features
            n_results: Number of results to return
            where: Filter conditions
            where_document: Document filter conditions
            
        Returns:
            Query results
        """
        endpoint = f"collections/{collection_name}/query"
        payload = {
            "query_features": query_features,
            "n_results": n_results,
            "where": where,
            "where_document": where_document
        }
        return await self.post(endpoint, json=payload)
    
    async def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get collection statistics.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Collection statistics
        """
        endpoint = f"collections/{collection_name}/stats"
        return await self.get(endpoint)
    
    async def delete_from_collection(
        self,
        collection_name: str,
        ids: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Delete items from a collection.
        
        Args:
            collection_name: Name of the collection
            ids: List of document IDs to delete
            where: Filter conditions
            where_document: Document filter conditions
            
        Returns:
            Operation result
        """
        endpoint = f"collections/{collection_name}/delete"
        payload = {
            "ids": ids,
            "where": where,
            "where_document": where_document
        }
        return await self.post(endpoint, json=payload) 