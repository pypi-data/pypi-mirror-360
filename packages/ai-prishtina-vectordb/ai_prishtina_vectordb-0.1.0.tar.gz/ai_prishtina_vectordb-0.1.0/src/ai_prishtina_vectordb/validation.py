"""
Validation functionality for AIPrishtina VectorDB.
"""

from typing import Any, Dict, List, Optional, Union
import numpy as np
from .exceptions import ValidationError
import asyncio
from concurrent.futures import ThreadPoolExecutor

class Validator:
    """Validator for AIPrishtina VectorDB operations."""
    
    def __init__(self):
        """Initialize validator."""
        self._executor = ThreadPoolExecutor(max_workers=4)
        
    async def validate_metadata(self, metadata: Dict[str, Any]) -> None:
        """Validate metadata dictionary.
        
        Args:
            metadata: Metadata dictionary to validate
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(metadata, dict):
            raise ValidationError("Metadata must be a dictionary")
            
        for key, value in metadata.items():
            if not isinstance(key, str):
                raise ValidationError(f"Metadata key must be string, got {type(key)}")
            if not isinstance(value, (str, int, float, bool, list, dict, type(None))):
                raise ValidationError(f"Invalid metadata value type: {type(value)}")
                
    async def validate_documents(self, documents: List[str]) -> None:
        """Validate document list.
        
        Args:
            documents: List of documents to validate
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(documents, list):
            raise ValidationError("Documents must be a list")
            
        if not documents:
            raise ValidationError("Documents list cannot be empty")
            
        for doc in documents:
            if not isinstance(doc, str):
                raise ValidationError(f"Document must be string, got {type(doc)}")
            if not doc.strip():
                raise ValidationError("Document cannot be empty")
                
    async def validate_embeddings(self, embeddings: np.ndarray) -> None:
        """Validate embeddings array.
        
        Args:
            embeddings: Embeddings array to validate
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(embeddings, np.ndarray):
            raise ValidationError("Embeddings must be numpy array")
            
        if embeddings.ndim != 2:
            raise ValidationError(f"Embeddings must be 2D array, got {embeddings.ndim}D")
            
        if embeddings.shape[0] == 0:
            raise ValidationError("Embeddings array cannot be empty")
            
        if np.isnan(embeddings).any():
            raise ValidationError("Embeddings cannot contain NaN values")
            
    async def validate_query_params(
        self,
        n_results: int,
        where: Optional[Dict[str, Any]] = None
    ) -> None:
        """Validate query parameters.
        
        Args:
            n_results: Number of results to return
            where: Filter conditions
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(n_results, int):
            raise ValidationError("n_results must be integer")
            
        if n_results <= 0:
            raise ValidationError("n_results must be positive")
            
        if where is not None:
            await self.validate_metadata(where)
            
    async def validate_index_params(
        self,
        index_type: str,
        **kwargs
    ) -> None:
        """Validate index parameters.
        
        Args:
            index_type: Type of index
            **kwargs: Additional index parameters
            
        Raises:
            ValidationError: If validation fails
        """
        valid_types = ["hnsw", "flat", "ivf"]
        if index_type not in valid_types:
            raise ValidationError(f"Invalid index type: {index_type}")
            
        if index_type == "hnsw":
            if "M" in kwargs and not isinstance(kwargs["M"], int):
                raise ValidationError("M must be integer")
            if "ef_construction" in kwargs and not isinstance(kwargs["ef_construction"], int):
                raise ValidationError("ef_construction must be integer")
                
        elif index_type == "ivf":
            if "nlist" in kwargs and not isinstance(kwargs["nlist"], int):
                raise ValidationError("nlist must be integer")
                
    async def validate_ids(self, ids: List[str]) -> None:
        """Validate ID list.
        
        Args:
            ids: List of IDs to validate
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(ids, list):
            raise ValidationError("IDs must be a list")
            
        if not ids:
            raise ValidationError("IDs list cannot be empty")
            
        for id in ids:
            if not isinstance(id, str):
                raise ValidationError(f"ID must be string, got {type(id)}")
            if not id.strip():
                raise ValidationError("ID cannot be empty")
                
    async def validate_batch_size(self, batch_size: int) -> None:
        """Validate batch size.
        
        Args:
            batch_size: Batch size to validate
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(batch_size, int):
            raise ValidationError("Batch size must be integer")
            
        if batch_size <= 0:
            raise ValidationError("Batch size must be positive")
            
    async def validate_dimension(self, dimension: int) -> None:
        """Validate vector dimension.
        
        Args:
            dimension: Vector dimension to validate
            
        Raises:
            ValidationError: If validation fails
        """
        if not isinstance(dimension, int):
            raise ValidationError("Dimension must be integer")
            
        if dimension <= 0:
            raise ValidationError("Dimension must be positive")
            
    def __del__(self):
        """Cleanup executor on deletion."""
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=False)

# Create global validator instance
validator = Validator()

# Export validation functions
async def validate_metadata(metadata: Dict[str, Any]) -> None:
    """Validate metadata dictionary."""
    await validator.validate_metadata(metadata)

async def validate_documents(documents: List[str]) -> None:
    """Validate document list."""
    await validator.validate_documents(documents)

async def validate_embeddings(embeddings: np.ndarray) -> None:
    """Validate embeddings array."""
    await validator.validate_embeddings(embeddings)

async def validate_query_params(
    n_results: int,
    where: Optional[Dict[str, Any]] = None
) -> None:
    """Validate query parameters."""
    await validator.validate_query_params(n_results, where)

async def validate_index_params(index_type: str, **kwargs) -> None:
    """Validate index parameters."""
    await validator.validate_index_params(index_type, **kwargs)

async def validate_ids(ids: List[str]) -> None:
    """Validate ID list."""
    await validator.validate_ids(ids)

async def validate_batch_size(batch_size: int) -> None:
    """Validate batch size."""
    await validator.validate_batch_size(batch_size)

async def validate_dimension(dimension: int) -> None:
    """Validate vector dimension."""
    await validator.validate_dimension(dimension)

def validate_metadata(metadata: Union[Dict[str, Any], List[Dict[str, Any]]]) -> bool:
    """Validate metadata.
    
    Args:
        metadata: Metadata dictionary or list of metadata dictionaries
        
    Returns:
        bool: True if validation passes
        
    Raises:
        ValidationError: If metadata is invalid
    """
    if isinstance(metadata, dict):
        if not all(isinstance(k, str) for k in metadata.keys()):
            raise ValidationError("Metadata keys must be strings")
        if not all(isinstance(v, (str, int, float, bool)) for v in metadata.values()):
            raise ValidationError("Metadata values must be strings, numbers, or booleans")
    elif isinstance(metadata, list):
        if not all(isinstance(m, dict) for m in metadata):
            raise ValidationError("All metadata items must be dictionaries")
        for m in metadata:
            validate_metadata(m)
    else:
        raise ValidationError("Metadata must be a dictionary or list of dictionaries")
    return True

def validate_documents(
    documents: List[str],
    metadatas: Optional[List[Dict[str, Any]]] = None,
    ids: Optional[List[str]] = None
) -> bool:
    """Validate documents and associated metadata/IDs.
    
    Args:
        documents: List of document texts
        metadatas: Optional list of metadata dictionaries
        ids: Optional list of document IDs
        
    Returns:
        bool: True if validation passes
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(documents, list):
        raise ValidationError("Documents must be a list")
    if not all(isinstance(d, str) for d in documents):
        raise ValidationError("All documents must be strings")
        
    if metadatas is not None:
        if not isinstance(metadatas, list):
            raise ValidationError("Metadatas must be a list")
        if len(metadatas) != len(documents):
            raise ValidationError("Number of metadatas must match number of documents")
        validate_metadata(metadatas)
        
    if ids is not None:
        if not isinstance(ids, list):
            raise ValidationError("IDs must be a list")
        if len(ids) != len(documents):
            raise ValidationError("Number of IDs must match number of documents")
        if not all(isinstance(i, str) for i in ids):
            raise ValidationError("All IDs must be strings")
        if len(set(ids)) != len(ids):
            raise ValidationError("IDs must be unique")
    return True

def validate_embeddings(embeddings: np.ndarray) -> None:
    """Validate embeddings array."""
    if not isinstance(embeddings, np.ndarray):
        raise ValidationError("Embeddings must be a numpy array")
    
    if len(embeddings.shape) != 2:
        raise ValidationError("Embeddings must be a 2D array")
    
    if np.isnan(embeddings).any():
        raise ValidationError("Embeddings cannot contain NaN values")

def validate_query_params(
    query_texts: Optional[List[str]] = None,
    query_embeddings: Optional[np.ndarray] = None,
    n_results: int = 5,
    where: Optional[Dict[str, Any]] = None
) -> None:
    """Validate query parameters."""
    if query_texts is None and query_embeddings is None:
        raise ValidationError("Either query_texts or query_embeddings must be provided")
    
    if query_texts is not None:
        validate_documents(query_texts)
    
    if query_embeddings is not None:
        validate_embeddings(query_embeddings)
    
    if not isinstance(n_results, int) or n_results <= 0:
        raise ValidationError("n_results must be a positive integer")
    
    if where is not None:
        validate_metadata(where)

def validate_batch_params(
    batch_size: int,
    max_workers: int
) -> None:
    """Validate batch processing parameters."""
    if not isinstance(batch_size, int) or batch_size <= 0:
        raise ValidationError("batch_size must be a positive integer")
    
    if not isinstance(max_workers, int) or max_workers <= 0:
        raise ValidationError("max_workers must be a positive integer")

def validate_index_params(
    index_type: str,
    params: Dict[str, Any]
) -> None:
    """Validate index parameters."""
    valid_types = {"hnsw", "ivf", "flat"}
    if index_type not in valid_types:
        raise ValidationError(f"Invalid index type. Must be one of: {valid_types}")
    
    if not isinstance(params, dict):
        raise ValidationError("Index parameters must be a dictionary")
    
    if index_type == "hnsw":
        required_params = {"M", "ef_construction", "ef_search"}
        missing = required_params - set(params.keys())
        if missing:
            raise ValidationError(f"Missing required HNSW parameters: {missing}")
    
    elif index_type == "ivf":
        required_params = {"nlist", "nprobe"}
        missing = required_params - set(params.keys())
        if missing:
            raise ValidationError(f"Missing required IVF parameters: {missing}")

def validate_ids(ids: List[str]) -> bool:
    """Validate document IDs.
    
    Args:
        ids: List of document IDs
        
    Returns:
        bool: True if validation passes
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(ids, list):
        raise ValidationError("IDs must be a list")
    if not all(isinstance(i, str) for i in ids):
        raise ValidationError("All IDs must be strings")
    if not all(i.strip() for i in ids):
        raise ValidationError("IDs cannot be empty strings")
    if len(set(ids)) != len(ids):
        raise ValidationError("IDs must be unique")
    return True

def validate_lengths(
    documents: List[str],
    metadatas: Optional[List[Dict[str, Any]]] = None,
    ids: Optional[List[str]] = None
) -> bool:
    """Validate lengths of documents, metadatas, and IDs.
    
    Args:
        documents: List of document texts
        metadatas: Optional list of metadata dictionaries
        ids: Optional list of document IDs
        
    Returns:
        bool: True if validation passes
        
    Raises:
        ValidationError: If lengths don't match
    """
    if metadatas is not None and len(metadatas) != len(documents):
        raise ValidationError("Number of metadatas must match number of documents")
    if ids is not None and len(ids) != len(documents):
        raise ValidationError("Number of IDs must match number of documents")
    return True 