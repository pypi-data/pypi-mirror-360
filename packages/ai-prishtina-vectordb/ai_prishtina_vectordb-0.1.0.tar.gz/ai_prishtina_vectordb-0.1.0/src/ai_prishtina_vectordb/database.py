"""
Vector database functionality for the AIPrishtina VectorDB library.
"""

from typing import Any, Dict, List, Optional, Union
import numpy as np
import chromadb
from chromadb.utils import embedding_functions
from .data_sources import DataSource
from .validation import (
    validate_metadata,
    validate_documents,
    validate_embeddings,
    validate_query_params,
    validate_index_params,
    validate_ids
)
from .exceptions import DatabaseError, ValidationError
import os
from pathlib import Path
from .config import DatabaseConfig
from .logger import AIPrishtinaLogger
from datetime import datetime
import json
import tempfile
import asyncio
from concurrent.futures import ThreadPoolExecutor

class Database:
    """
    A professional vector database for storing and querying vector embeddings.
    
    This class provides a unified interface for vector storage and similarity search,
    supporting various data sources and indexing methods.
    """
    
    def __init__(
        self,
        collection_name: str = "default",
        config: Optional[Dict[str, Any]] = None
    ):
        """Initialize database.
        
        Args:
            collection_name: Name of the collection
            config: Configuration dictionary
        """
        self.logger = AIPrishtinaLogger()
        self.config = config or {}
        self.collection_name = collection_name
        self._executor = ThreadPoolExecutor(max_workers=4)
        
        # Initialize ChromaDB client with minimal settings
        try:
            import chromadb
            from chromadb.utils import embedding_functions
            
            # Create a temporary directory for persistence
            persist_dir = tempfile.mkdtemp()
            
            # Initialize client using new API
            self.client = chromadb.PersistentClient(path=persist_dir)
            
            # Use a simple embedding function for testing that doesn't require model download
            embedding_function = embedding_functions.DefaultEmbeddingFunction()
            
            # Create or get collection with minimal metadata
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                embedding_function=embedding_function,
                metadata={
                    "embedding_model": "default",
                    "index_type": "default"
                }
            )
            asyncio.create_task(self.logger.info(f"Initialized database with collection: {collection_name}"))
        except Exception as e:
            asyncio.create_task(self.logger.error(f"Failed to initialize database: {str(e)}"))
            raise DatabaseError(f"Failed to initialize database: {str(e)}")

    async def add_from_source(
        self,
        source: Union[str, List[Dict[str, Any]]],
        source_type: str = "text",
        text_column: Optional[str] = None,
        metadata_columns: Optional[List[str]] = None,
        **kwargs
    ) -> None:
        """
        Add data from various sources to the database.
        
        Args:
            source: Data source (file path, DataFrame, or list of dicts)
            source_type: Type of data source ('text', 'json', 'csv', 'pandas')
            text_column: Column name containing text to vectorize
            metadata_columns: Columns to include as metadata
            **kwargs: Additional parameters for data loading
        """
        try:
            async with DataSource(source_type=source_type, **kwargs) as data_source:
                data = await data_source.load_data(
                    source=source,
                    text_column=text_column,
                    metadata_columns=metadata_columns,
                    **kwargs
                )
                
                # Validate data
                validate_documents(data['documents'])
                for metadata in data['metadatas']:
                    validate_metadata(metadata)
                
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(
                    self._executor,
                    lambda: self.collection.add(
                        documents=data['documents'],
                        metadatas=data['metadatas'],
                        ids=data['ids']
                    )
                )
                await self.logger.info(f"Added {len(data['documents'])} documents to collection")
        except Exception as e:
            raise DatabaseError(f"Failed to add data from source: {str(e)}")

    async def add(
        self,
        embeddings: Optional[np.ndarray] = None,
        documents: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> None:
        """
        Add vectors to the database.
        
        Args:
            embeddings: Optional vector embeddings to add
            documents: Optional documents associated with the embeddings
            metadatas: Optional metadata for each embedding
            ids: Optional IDs for each embedding
        """
        try:
            if embeddings is None and documents is None:
                raise ValidationError("Either embeddings or documents must be provided")

            if ids is None:
                length = len(documents) if documents is not None else len(embeddings)
                ids = [str(i) for i in range(length)]

            if metadatas is None:
                metadatas = [{"type": "default"} for _ in range(len(ids))]

            # Validate inputs
            if documents is not None:
                validate_documents(documents)
            if embeddings is not None:
                validate_embeddings(embeddings)
            for metadata in metadatas:
                validate_metadata(metadata)

            if embeddings is None and documents is not None:
                # Generate embeddings from documents
                loop = asyncio.get_event_loop()
                embeddings = await loop.run_in_executor(
                    self._executor,
                    lambda: self.collection._embedding_function(documents)
                )

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self._executor,
                lambda: self.collection.add(
                    embeddings=embeddings.tolist() if isinstance(embeddings, np.ndarray) else embeddings,
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )
            )
            await self.logger.info(f"Added {len(documents) if documents is not None else len(embeddings)} vectors to collection")
        except Exception as e:
            raise DatabaseError(f"Failed to add vectors: {str(e)}")

    async def query(
        self,
        query_texts: Optional[List[str]] = None,
        query_embeddings: Optional[np.ndarray] = None,
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Query the database for similar vectors.
        
        Args:
            query_texts: Optional query texts
            query_embeddings: Optional query vector embeddings
            n_results: Number of results to return
            where: Optional filter conditions
            **kwargs: Additional query parameters
            
        Returns:
            Dict containing query results
        """
        try:
            validate_query_params(n_results, where)
            
            if query_texts is None and query_embeddings is None:
                raise ValidationError("Either query_texts or query_embeddings must be provided")
            
            if query_embeddings is None and query_texts is not None:
                # Generate embeddings from query texts
                loop = asyncio.get_event_loop()
                query_embeddings = await loop.run_in_executor(
                    self._executor,
                    lambda: self.collection._embedding_function(query_texts)
                )
            
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                self._executor,
                lambda: self.collection.query(
                    query_embeddings=query_embeddings.tolist() if isinstance(query_embeddings, np.ndarray) else query_embeddings,
                    n_results=n_results,
                    where=where,
                    **kwargs
                )
            )
            
            await self.logger.info(f"Query returned {len(results['ids'][0])} results")
            return results
        except Exception as e:
            raise DatabaseError(f"Failed to query database: {str(e)}")

    async def delete(
        self,
        ids: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Delete vectors from the database.
        
        Args:
            ids: Optional list of IDs to delete
            where: Optional filter conditions
        """
        try:
            if ids is not None:
                validate_ids(ids)
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self._executor,
                lambda: self.collection.delete(
                    ids=ids,
                    where=where
                )
            )
            await self.logger.info(f"Deleted vectors from collection")
        except Exception as e:
            raise DatabaseError(f"Failed to delete vectors: {str(e)}")

    async def get(
        self,
        ids: Optional[List[str]] = None,
        where: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Get vectors from the database.
        
        Args:
            ids: Optional list of IDs to get
            where: Optional filter conditions
            **kwargs: Additional parameters
            
        Returns:
            Dict containing retrieved vectors
        """
        try:
            if ids is not None:
                validate_ids(ids)
            
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                self._executor,
                lambda: self.collection.get(
                    ids=ids,
                    where=where,
                    **kwargs
                )
            )
            
            await self.logger.info(f"Retrieved {len(results['ids'])} vectors from collection")
            return results
        except Exception as e:
            raise DatabaseError(f"Failed to get vectors: {str(e)}")

    async def update(
        self,
        ids: List[str],
        embeddings: Optional[np.ndarray] = None,
        documents: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Update vectors in the database.
        
        Args:
            ids: List of IDs to update
            embeddings: Optional new embeddings
            documents: Optional new documents
            metadatas: Optional new metadata
        """
        try:
            validate_ids(ids)
            
            if embeddings is None and documents is None and metadatas is None:
                raise ValidationError("At least one of embeddings, documents, or metadatas must be provided")
            
            if embeddings is None and documents is not None:
                # Generate embeddings from documents
                loop = asyncio.get_event_loop()
                embeddings = await loop.run_in_executor(
                    self._executor,
                    lambda: self.collection._embedding_function(documents)
                )
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self._executor,
                lambda: self.collection.update(
                    ids=ids,
                    embeddings=embeddings.tolist() if isinstance(embeddings, np.ndarray) else embeddings,
                    documents=documents,
                    metadatas=metadatas
                )
            )
            await self.logger.info(f"Updated {len(ids)} vectors in collection")
        except Exception as e:
            raise DatabaseError(f"Failed to update vectors: {str(e)}")

    async def create_index(
        self,
        index_type: str = "hnsw",
        **kwargs
    ) -> None:
        """
        Create an index for the collection.
        
        Args:
            index_type: Type of index to create
            **kwargs: Additional index parameters
        """
        try:
            validate_index_params(index_type, **kwargs)
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self._executor,
                lambda: self.collection.create_index(
                    index_type=index_type,
                    **kwargs
                )
            )
            await self.logger.info(f"Created {index_type} index for collection")
        except Exception as e:
            raise DatabaseError(f"Failed to create index: {str(e)}")

    async def delete_collection(self) -> None:
        """Delete the collection."""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self._executor,
                lambda: self.client.delete_collection(self.collection_name)
            )
            await self.logger.info(f"Deleted collection: {self.collection_name}")
        except Exception as e:
            raise DatabaseError(f"Failed to delete collection: {str(e)}")

    def __del__(self):
        """Cleanup when the object is destroyed."""
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=False) 