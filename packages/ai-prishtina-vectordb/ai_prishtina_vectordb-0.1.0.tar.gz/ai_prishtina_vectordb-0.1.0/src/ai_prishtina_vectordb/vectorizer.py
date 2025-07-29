"""
Core vectorization functionality for the AIPrishtina VectorDB library.
"""

from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd
from .embeddings import EmbeddingModel
from sklearn.preprocessing import OneHotEncoder, LabelEncoder
from sklearn.feature_extraction import FeatureHasher
import asyncio
from concurrent.futures import ThreadPoolExecutor
from .logger import AIPrishtinaLogger
from .exceptions import VectorizationError

class Vectorizer:
    """
    A professional vectorizer for converting various data types into vector embeddings.
    
    This class provides methods to vectorize different types of data including:
    - Text data
    - Numerical data
    - Categorical data
    - Mixed data types
    """
    
    def __init__(self, embedding_model: Optional[EmbeddingModel] = None):
        """Initialize the vectorizer.
        
        Args:
            embedding_model: Optional embedding model to use
        """
        self.embedding_model = embedding_model or EmbeddingModel()
        self.logger = AIPrishtinaLogger()
        self._executor = ThreadPoolExecutor(max_workers=4)

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=False)

    def __del__(self):
        """Cleanup on deletion."""
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=False)

    async def vectorize_text(self, text: str) -> np.ndarray:
        """Vectorize text data.
        
        Args:
            text: Text to vectorize
            
        Returns:
            Vector representation of the text
        """
        try:
            embeddings = await self.embedding_model.encode([text])
            return embeddings[0]
        except Exception as e:
            await self.logger.error(f"Failed to vectorize text: {str(e)}")
            raise VectorizationError(f"Failed to vectorize text: {str(e)}")

    async def vectorize_numerical(self, data: np.ndarray) -> np.ndarray:
        """Vectorize numerical data.
        
        Args:
            data: Numerical data to vectorize
            
        Returns:
            Vector representation of the numerical data
        """
        try:
            # Normalize numerical data
            normalized = await self._normalize_vectors(data)
            return normalized
        except Exception as e:
            await self.logger.error(f"Failed to vectorize numerical data: {str(e)}")
            raise VectorizationError(f"Failed to vectorize numerical data: {str(e)}")

    async def vectorize_categorical(self, data: List[str]) -> np.ndarray:
        """Vectorize categorical data.
        
        Args:
            data: Categorical data to vectorize
            
        Returns:
            Vector representation of the categorical data
        """
        try:
            # Convert categorical data to text and vectorize
            text = " ".join(data)
            return await self.vectorize_text(text)
        except Exception as e:
            await self.logger.error(f"Failed to vectorize categorical data: {str(e)}")
            raise VectorizationError(f"Failed to vectorize categorical data: {str(e)}")

    async def _normalize_vectors(self, vectors: np.ndarray) -> np.ndarray:
        """Normalize vectors.
        
        Args:
            vectors: Vectors to normalize
            
        Returns:
            Normalized vectors
        """
        try:
            # Run normalization in thread pool
            loop = asyncio.get_event_loop()
            normalized = await loop.run_in_executor(
                self._executor,
                lambda: vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
            )
            return normalized
        except Exception as e:
            await self.logger.error(f"Failed to normalize vectors: {str(e)}")
            raise VectorizationError(f"Failed to normalize vectors: {str(e)}")

    async def vectorize_text(
        self,
        texts: Union[str, List[str]],
        batch_size: int = 32,
        **kwargs
    ) -> np.ndarray:
        """
        Vectorize text data using the embedding model.
        
        Args:
            texts: Single text or list of texts to vectorize
            batch_size: Batch size for processing
            **kwargs: Additional parameters for the embedding model
            
        Returns:
            numpy.ndarray: Vector embeddings
        """
        if isinstance(texts, str):
            texts = [texts]
            
        embeddings = await self.embedding_model.encode(texts, batch_size=batch_size, **kwargs)
        
        if self.normalize:
            embeddings = await self._normalize_vectors(embeddings)
            
        return embeddings

    async def vectorize_numerical(
        self,
        data: Union[np.ndarray, pd.DataFrame],
        method: str = "standard",
        **kwargs
    ) -> np.ndarray:
        """
        Vectorize numerical data using various methods.
        
        Args:
            data: Numerical data to vectorize
            method: Vectorization method ('standard', 'minmax', 'robust')
            **kwargs: Additional parameters for the vectorization method
            
        Returns:
            numpy.ndarray: Vector embeddings
        """
        if isinstance(data, pd.DataFrame):
            data = data.values
            
        loop = asyncio.get_event_loop()
        
        if method == "standard":
            from sklearn.preprocessing import StandardScaler
            scaler = StandardScaler(**kwargs)
        elif method == "minmax":
            from sklearn.preprocessing import MinMaxScaler
            scaler = MinMaxScaler(**kwargs)
        elif method == "robust":
            from sklearn.preprocessing import RobustScaler
            scaler = RobustScaler(**kwargs)
        else:
            raise ValueError(f"Unknown method: {method}")
            
        vectors = await loop.run_in_executor(
            self._executor,
            lambda: scaler.fit_transform(data)
        )
        
        if self.normalize:
            vectors = await self._normalize_vectors(vectors)
            
        return vectors

    async def vectorize_categorical(
        self,
        data: Union[List[str], np.ndarray],
        method: str = "onehot",
        **kwargs
    ) -> np.ndarray:
        """
        Vectorize categorical data.

        Args:
            data: Categorical data to vectorize
            method: Vectorization method ('onehot', 'label', or 'hash')
            **kwargs: Additional parameters for the vectorization method

        Returns:
            Vectorized data as numpy array
        """
        loop = asyncio.get_event_loop()
        
        if method == "onehot":
            encoder = OneHotEncoder(sparse_output=False, **kwargs)
            data_array = np.array(data).reshape(-1, 1)
            vectors = await loop.run_in_executor(
                self._executor,
                lambda: encoder.fit_transform(data_array)
            )
        elif method == "label":
            encoder = LabelEncoder()
            vectors = await loop.run_in_executor(
                self._executor,
                lambda: encoder.fit_transform(data).reshape(-1, 1)
            )
        elif method == "hash":
            hasher = FeatureHasher(n_features=kwargs.get("n_features", 10))
            vectors = await loop.run_in_executor(
                self._executor,
                lambda: hasher.transform([{str(i): x} for i, x in enumerate(data)]).toarray()
            )
        else:
            raise ValueError(f"Unknown vectorization method: {method}")

        return vectors 