"""Tests for feature extraction functionality."""

import pytest
import numpy as np
import os
import shutil
from ai_prishtina_vectordb.features import (
    FeatureConfig,
    FeatureExtractor,
    TextFeatureExtractor,
    FeatureProcessor,
    FeatureRegistry
)
from ai_prishtina_vectordb.exceptions import FeatureError
import unittest.mock
from typing import Dict, Any

@pytest.fixture(scope="function")
def test_db_dir(tmp_path):
    """Create a temporary directory for the test database."""
    db_dir = tmp_path / "test_chroma_db"
    db_dir.mkdir(exist_ok=True)
    yield str(db_dir)
    # Cleanup after test
    if os.path.exists(db_dir):
        shutil.rmtree(db_dir)

@pytest.fixture
def feature_config():
    return FeatureConfig(
        normalize=True,
        dimensionality_reduction=None,
        feature_scaling=True,
        cache_features=True,
        batch_size=100,
        device="cpu",
        collection_name="test_features",
        collection_metadata={"description": "Test collection"},
        distance_function="cosine",
        embedding_function="all-MiniLM-L6-v2"
    )

@pytest.fixture
def text_extractor(feature_config):
    """Create a text feature extractor."""
    return TextFeatureExtractor(feature_config)

@pytest.fixture
def feature_processor(feature_config):
    """Create a feature processor."""
    processor = FeatureProcessor(feature_config)
    yield processor
    # Cleanup after test
    if processor.client:
        processor.client.reset()

@pytest.fixture
def feature_registry():
    """Create a feature registry."""
    return FeatureRegistry()

@pytest.mark.asyncio
async def test_feature_config_defaults():
    """Test feature configuration defaults."""
    config = FeatureConfig()
    assert config.normalize is True
    assert config.dimensionality_reduction is None
    assert config.feature_scaling is True
    assert config.cache_features is True
    assert config.batch_size == 100
    assert config.device == "cpu"
    assert config.collection_name == "features"
    assert config.distance_function == "cosine"
    assert config.embedding_function == "all-MiniLM-L6-v2"

@pytest.mark.asyncio
async def test_text_feature_extraction(feature_config):
    """Test text feature extraction."""
    extractor = TextFeatureExtractor(feature_config)
    text = "Test feature extraction"
    features = await extractor.extract_text(text)
    assert isinstance(features, np.ndarray)
    assert len(features.shape) == 1

@pytest.mark.asyncio
async def test_batch_text_extraction(feature_config):
    """Test batch text feature extraction."""
    extractor = TextFeatureExtractor(feature_config)
    texts = ["Test 1", "Test 2", "Test 3"]
    features = await extractor.extract_text_batch(texts)
    assert isinstance(features, np.ndarray)
    assert len(features) == len(texts)

@pytest.mark.skip(reason="Feature processor collection operations test temporarily disabled")
@pytest.mark.asyncio
async def test_feature_processor_collection_operations():
    """Test feature processor collection operations."""
    config = FeatureConfig(
        collection_name="test_collection",
        embedding_function="all-MiniLM-L6-v2",
        persist_directory=".chroma"
    )
    processor = FeatureProcessor(config)
    await processor._init_extractors()

    # Test data
    test_data = {
        "text": "Test document",
        "metadata": {"source": "test"}
    }

    # Add to collection
    doc_id = await processor.add_to_collection(
        documents=[test_data["text"]],
        metadatas=[test_data["metadata"]]
    )
    assert doc_id == ["test_doc_1"]

    # Query collection
    results = await processor.query_collection(
        query_texts=["Test document"],
        n_results=1
    )
    assert len(results["documents"]) > 0
    assert results["documents"][0] == test_data["text"]
    assert results["metadatas"][0] == test_data["metadata"]

    # Cleanup
    await processor.close()

@pytest.mark.asyncio
async def test_feature_processor_error_handling(feature_config):
    """Test error handling in feature processor."""
    processor = FeatureProcessor(feature_config)
    
    # Test processing empty data
    with pytest.raises(FeatureError):
        await processor.process({})
    
    # Test collection operations without collection
    with pytest.raises(FeatureError):
        await processor.query_collection("test", n_results=1)

@pytest.mark.asyncio
async def test_feature_registry():
    """Test feature registry."""
    registry = FeatureRegistry()
    
    # Create test extractor
    class TestExtractor(FeatureExtractor):
        async def extract(self, data: Dict[str, Any]) -> np.ndarray:
            return np.array([1.0, 2.0, 3.0])
    
    # Register extractor
    extractor = TestExtractor()
    registry.register_extractor("test", extractor)
    
    # Get extractor
    retrieved_extractor = registry.get_extractor("test")
    assert retrieved_extractor is not None
    
    # Test extraction
    features = await retrieved_extractor.extract({"test": "data"})
    assert isinstance(features, np.ndarray)
    assert features.shape == (3,)
    
    # Test processor registration
    config = FeatureConfig()
    processor = FeatureProcessor(config)
    registry.register_processor("test", processor)
    
    # Get processor
    retrieved_processor = registry.get_processor("test")
    assert retrieved_processor is not None
    
    # Test processing
    result = await retrieved_processor.process({"text": "test data"})
    assert isinstance(result, np.ndarray)

@pytest.mark.skip(reason="Dimensionality reduction test temporarily disabled")
def test_dimensionality_reduction(feature_processor):
    """Test dimensionality reduction in feature processor."""
    config = FeatureConfig(
        dimensionality_reduction=64,
        collection_name="reduced_collection",
        persist_directory="./test_chroma_db"
    )
    processor = FeatureProcessor(config)
    
    data = {"text": "This is a test text for dimensionality reduction"}
    features = processor.process(data)
    assert len(features) == 64

@pytest.mark.skip(reason="Feature scaling test temporarily disabled")
def test_feature_scaling(feature_processor):
    """Test feature scaling in feature processor."""
    config = FeatureConfig(
        feature_scaling=True,
        collection_name="scaled_collection",
        persist_directory="./test_chroma_db"
    )
    processor = FeatureProcessor(config)
    
    data = {"text": "Test text for scaling"}
    features = processor.process(data)
    assert np.all(features >= 0) and np.all(features <= 1) 