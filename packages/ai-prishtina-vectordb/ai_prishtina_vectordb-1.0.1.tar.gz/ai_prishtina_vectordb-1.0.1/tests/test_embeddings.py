"""
Unit tests for embedding functionality in AIPrishtina VectorDB.
"""

import pytest
import numpy as np
from ai_prishtina_vectordb.embeddings import EmbeddingModel

@pytest.fixture
async def embedding_model():
    """Fixture to create an embedding model."""
    model = EmbeddingModel()
    yield model
    # Cleanup if needed
    await model.close()

@pytest.mark.asyncio
async def test_text_embeddings(embedding_model):
    """Test text embedding generation."""
    texts = ["Hello world", "Test embedding"]
    embeddings = await embedding_model.embed_text(texts)
    
    assert isinstance(embeddings, np.ndarray)
    assert len(embeddings) == len(texts)
    assert np.all(np.isfinite(embeddings))

@pytest.mark.asyncio
async def test_image_embeddings(embedding_model):
    """Test image embedding generation."""
    # Create a dummy image array
    image = np.random.rand(224, 224, 3)
    embedding = await embedding_model.embed_image(image)
    
    assert isinstance(embedding, np.ndarray)
    assert np.all(np.isfinite(embedding))

@pytest.mark.asyncio
async def test_audio_embeddings(embedding_model):
    """Test audio embedding generation."""
    # Create a dummy audio array
    audio = np.random.rand(16000)  # 1 second of audio at 16kHz
    embedding = await embedding_model.embed_audio(audio)
    
    assert isinstance(embedding, np.ndarray)
    assert np.all(np.isfinite(embedding))

@pytest.mark.asyncio
async def test_video_embeddings(embedding_model):
    """Test video embedding generation."""
    # Create a dummy video array
    video = np.random.rand(30, 224, 224, 3)  # 30 frames
    embedding = await embedding_model.embed_video(video)
    
    assert isinstance(embedding, np.ndarray)
    assert np.all(np.isfinite(embedding))

@pytest.mark.asyncio
async def test_embedding_dimensions(embedding_model):
    """Test embedding dimensions."""
    text = "Test embedding dimensions"
    embedding = await embedding_model.embed_text([text])
    
    assert len(embedding.shape) == 2
    assert embedding.shape[0] == 1  # Batch size
    assert embedding.shape[1] > 0  # Embedding dimension

@pytest.mark.asyncio
async def test_embedding_normalization(embedding_model):
    """Test embedding normalization."""
    text = "Test embedding normalization"
    embedding = await embedding_model.embed_text([text])
    
    norm = np.linalg.norm(embedding, axis=1)
    np.testing.assert_array_almost_equal(norm, np.ones_like(norm))

if __name__ == '__main__':
    pytest.main() 