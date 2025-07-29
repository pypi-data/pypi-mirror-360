"""
Unit tests for the vectorizer module of AIPrishtina VectorDB.
"""

import numpy as np
import pytest
from ai_prishtina_vectordb.vectorizer import Vectorizer
from ai_prishtina_vectordb.embeddings import EmbeddingModel

@pytest.fixture
async def vectorizer():
    """Create a Vectorizer instance for testing."""
    vectorizer = Vectorizer()
    return vectorizer

@pytest.fixture
async def embedding_model():
    """Create an EmbeddingModel instance for testing."""
    model = EmbeddingModel()
    return model

@pytest.mark.asyncio
async def test_vectorize_text(vectorizer):
    """Test text vectorization."""
    texts = ["Hello world", "Test vectorization"]
    vectors = await vectorizer.vectorize_text(texts)
    
    assert isinstance(vectors, np.ndarray)
    assert len(vectors) == len(texts)
    assert np.all(np.isfinite(vectors))

@pytest.mark.asyncio
async def test_vectorize_numerical(vectorizer):
    """Test numerical data vectorization."""
    data = np.array([[1, 2, 3], [4, 5, 6]])
    vectors = await vectorizer.vectorize_numerical(data)
    
    assert isinstance(vectors, np.ndarray)
    assert vectors.shape == data.shape
    assert np.all(np.isfinite(vectors))

@pytest.mark.asyncio
async def test_vectorize_categorical(vectorizer):
    """Test categorical data vectorization."""
    categories = ["A", "B", "C", "A"]
    vectors = await vectorizer.vectorize_categorical(categories)
    
    assert isinstance(vectors, np.ndarray)
    assert len(vectors) == len(categories)
    assert np.all(np.isfinite(vectors))

@pytest.mark.asyncio
async def test_normalize_vectors(vectorizer):
    """Test vector normalization."""
    vectors = np.array([[1, 2, 3], [4, 5, 6]])
    normalized = await vectorizer._normalize_vectors(vectors)
    
    assert isinstance(normalized, np.ndarray)
    assert normalized.shape == vectors.shape
    assert np.all(np.isfinite(normalized))
    
    # Check if vectors are normalized (unit length)
    norms = np.linalg.norm(normalized, axis=1)
    np.testing.assert_array_almost_equal(norms, np.ones_like(norms)) 