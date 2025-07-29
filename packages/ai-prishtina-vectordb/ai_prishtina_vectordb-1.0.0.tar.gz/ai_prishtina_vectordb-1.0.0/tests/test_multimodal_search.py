"""
Tests for multi-modal search capabilities.
"""

import pytest
import asyncio
import numpy as np
from unittest.mock import Mock, AsyncMock, patch
import tempfile
import os

from ai_prishtina_vectordb.multimodal_search import (
    MultiModalSearchEngine,
    SearchQuery,
    SearchResult,
    ModalityType
)
from ai_prishtina_vectordb.database import Database
from ai_prishtina_vectordb.features import FeatureConfig
from ai_prishtina_vectordb.logger import AIPrishtinaLogger
from ai_prishtina_vectordb.metrics import MetricsCollector


class TestMultiModalSearchEngine:
    """Test cases for MultiModalSearchEngine."""
    
    @pytest.fixture
    def mock_database(self):
        """Create mock database."""
        db = Mock(spec=Database)
        db.collection_name = "test_collection"
        db.query = AsyncMock(return_value={
            'ids': [['doc1', 'doc2', 'doc3']],
            'distances': [[0.1, 0.2, 0.3]],
            'documents': [['Document 1', 'Document 2', 'Document 3']],
            'metadatas': [[{'type': 'text'}, {'type': 'text'}, {'type': 'text'}]]
        })
        return db
    
    @pytest.fixture
    def feature_config(self):
        """Create feature configuration."""
        return FeatureConfig(
            cache_features=True,
            normalize=True
        )
    
    @pytest.fixture
    def logger(self):
        """Create logger."""
        return AIPrishtinaLogger(name="test_multimodal")
    
    @pytest.fixture
    def metrics(self):
        """Create metrics collector."""
        return MetricsCollector()
    
    @pytest.fixture
    def search_engine(self, mock_database, feature_config, logger, metrics):
        """Create multi-modal search engine."""
        engine = MultiModalSearchEngine(
            database=mock_database,
            feature_config=feature_config,
            logger=logger,
            metrics=metrics
        )
        return engine
    
    @pytest.mark.asyncio
    async def test_text_only_search(self, search_engine):
        """Test search with text only."""
        query = SearchQuery(text="machine learning")
        
        with patch.object(search_engine.text_embedder, 'encode', new_callable=AsyncMock) as mock_encode:
            mock_encode.return_value = [np.random.rand(384).astype(np.float32)]
            
            results = await search_engine.search(query, n_results=5)
            
            assert len(results) <= 5
            assert all(isinstance(result, SearchResult) for result in results)
            mock_encode.assert_called_once_with(["machine learning"])
    
    @pytest.mark.asyncio
    async def test_multimodal_search(self, search_engine):
        """Test search with multiple modalities."""
        # Create temporary files for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test document content")
            doc_path = f.name
        
        try:
            query = SearchQuery(
                text="machine learning",
                document_path=doc_path,
                modality_weights={
                    ModalityType.TEXT: 0.6,
                    ModalityType.DOCUMENT: 0.4
                }
            )
            
            with patch.object(search_engine.text_embedder, 'encode', new_callable=AsyncMock) as mock_encode:
                mock_encode.return_value = [np.random.rand(384).astype(np.float32)]
                
                results = await search_engine.search(query, n_results=3)
                
                assert len(results) <= 3
                assert all(isinstance(result, SearchResult) for result in results)
                
                # Check that modality scores are included
                for result in results:
                    assert isinstance(result.modality_scores, dict)
        
        finally:
            os.unlink(doc_path)
    
    @pytest.mark.asyncio
    async def test_search_with_similarity_threshold(self, search_engine):
        """Test search with similarity threshold."""
        query = SearchQuery(text="test query")
        
        with patch.object(search_engine.text_embedder, 'encode', new_callable=AsyncMock) as mock_encode:
            mock_encode.return_value = [np.random.rand(384).astype(np.float32)]
            
            results = await search_engine.search(
                query, 
                n_results=10, 
                similarity_threshold=0.5
            )
            
            # All results should have score >= threshold
            for result in results:
                assert result.score >= 0.5
    
    @pytest.mark.asyncio
    async def test_weighted_average_fusion(self, search_engine):
        """Test weighted average fusion strategy."""
        modality_results = {
            ModalityType.TEXT: {
                'ids': [['doc1', 'doc2']],
                'distances': [[0.2, 0.4]],
                'documents': [['Text 1', 'Text 2']],
                'metadatas': [[{'type': 'text'}, {'type': 'text'}]]
            },
            ModalityType.IMAGE: {
                'ids': [['doc1', 'doc3']],
                'distances': [[0.1, 0.3]],
                'documents': [['Image 1', 'Image 3']],
                'metadatas': [[{'type': 'image'}, {'type': 'image'}]]
            }
        }
        
        weights = {ModalityType.TEXT: 0.6, ModalityType.IMAGE: 0.4}
        
        results = await search_engine._weighted_average_fusion(modality_results, weights)
        
        assert len(results) >= 1
        assert all(isinstance(result, SearchResult) for result in results)
        
        # Check that scores are properly weighted
        for result in results:
            assert 0.0 <= result.score <= 1.0
    
    @pytest.mark.asyncio
    async def test_max_pooling_fusion(self, search_engine):
        """Test max pooling fusion strategy."""
        modality_results = {
            ModalityType.TEXT: {
                'ids': [['doc1', 'doc2']],
                'distances': [[0.2, 0.4]],
                'documents': [['Text 1', 'Text 2']],
                'metadatas': [[{'type': 'text'}, {'type': 'text'}]]
            }
        }
        
        weights = {ModalityType.TEXT: 1.0}
        
        results = await search_engine._max_pooling_fusion(modality_results, weights)
        
        assert len(results) >= 1
        assert all(isinstance(result, SearchResult) for result in results)
    
    @pytest.mark.asyncio
    async def test_extract_image_features(self, search_engine):
        """Test image feature extraction."""
        # Create a temporary image file path
        image_path = "/tmp/test_image.jpg"
        
        features = await search_engine._extract_image_features(image_path)
        
        assert isinstance(features, np.ndarray)
        assert features.shape == (512,)  # Expected feature dimension
        assert features.dtype == np.float32
    
    @pytest.mark.asyncio
    async def test_extract_audio_features(self, search_engine):
        """Test audio feature extraction."""
        audio_path = "/tmp/test_audio.wav"
        
        features = await search_engine._extract_audio_features(audio_path)
        
        assert isinstance(features, np.ndarray)
        assert features.shape == (256,)  # Expected feature dimension
        assert features.dtype == np.float32
    
    @pytest.mark.asyncio
    async def test_extract_video_features(self, search_engine):
        """Test video feature extraction."""
        video_path = "/tmp/test_video.mp4"
        
        features = await search_engine._extract_video_features(video_path)
        
        assert isinstance(features, np.ndarray)
        assert features.shape == (768,)  # Expected feature dimension
        assert features.dtype == np.float32
    
    @pytest.mark.asyncio
    async def test_extract_document_features(self, search_engine):
        """Test document feature extraction."""
        # Create temporary document
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test document with some content.")
            doc_path = f.name
        
        try:
            with patch.object(search_engine.text_embedder, 'encode', new_callable=AsyncMock) as mock_encode:
                mock_encode.return_value = [np.random.rand(384).astype(np.float32)]
                
                features = await search_engine._extract_document_features(doc_path)
                
                assert isinstance(features, np.ndarray)
                assert features.dtype == np.float32
                mock_encode.assert_called_once()
        
        finally:
            os.unlink(doc_path)
    
    @pytest.mark.asyncio
    async def test_search_modality(self, search_engine):
        """Test searching for a specific modality."""
        embedding = np.random.rand(384).astype(np.float32)
        
        results = await search_engine._search_modality(
            ModalityType.TEXT,
            embedding,
            n_results=5,
            metadata_filters={"type": "text"}
        )
        
        # Should return results from mock database
        search_engine.database.query.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_empty_query(self, search_engine):
        """Test search with empty query."""
        query = SearchQuery()  # No modalities specified
        
        with pytest.raises(Exception):  # Should raise SearchError
            await search_engine.search(query)
    
    @pytest.mark.asyncio
    async def test_custom_fusion_strategy(self, search_engine):
        """Test search with custom fusion strategy."""
        query = SearchQuery(
            text="test",
            fusion_strategy="attention_fusion"
        )
        
        with patch.object(search_engine.text_embedder, 'encode', new_callable=AsyncMock) as mock_encode:
            mock_encode.return_value = [np.random.rand(384).astype(np.float32)]
            
            results = await search_engine.search(query)
            
            assert isinstance(results, list)
    
    def test_search_query_creation(self):
        """Test SearchQuery creation and validation."""
        query = SearchQuery(
            text="test query",
            modality_weights={ModalityType.TEXT: 1.0},
            fusion_strategy="weighted_average"
        )
        
        assert query.text == "test query"
        assert query.modality_weights[ModalityType.TEXT] == 1.0
        assert query.fusion_strategy == "weighted_average"
    
    def test_search_result_creation(self):
        """Test SearchResult creation."""
        result = SearchResult(
            id="doc1",
            score=0.85,
            content={"text": "Document content"},
            metadata={"type": "text"},
            modality_scores={ModalityType.TEXT: 0.85}
        )
        
        assert result.id == "doc1"
        assert result.score == 0.85
        assert result.content["text"] == "Document content"
        assert result.modality_scores[ModalityType.TEXT] == 0.85
    
    @pytest.mark.asyncio
    async def test_search_with_metadata_filters(self, search_engine):
        """Test search with metadata filters."""
        query = SearchQuery(
            text="test",
            metadata_filters={"category": "science", "language": "en"}
        )
        
        with patch.object(search_engine.text_embedder, 'encode', new_callable=AsyncMock) as mock_encode:
            mock_encode.return_value = [np.random.rand(384).astype(np.float32)]
            
            await search_engine.search(query)
            
            # Verify that metadata filters were passed to database query
            search_engine.database.query.assert_called()
            call_args = search_engine.database.query.call_args
            assert "where" in call_args.kwargs or len(call_args.args) > 2
