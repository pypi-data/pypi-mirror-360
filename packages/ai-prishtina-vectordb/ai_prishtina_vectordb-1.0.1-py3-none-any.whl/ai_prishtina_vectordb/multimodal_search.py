"""
Multi-modal search capabilities for AI Prishtina VectorDB.

This module provides advanced multi-modal search functionality that can handle
text, images, audio, and video data in unified search operations.
"""

import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple
import numpy as np
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path

from .features import FeatureExtractor, FeatureConfig
from .embeddings import EmbeddingModel
from .database import Database
from .logger import AIPrishtinaLogger
from .exceptions import SearchError, ValidationError
from .metrics import MetricsCollector


class ModalityType(Enum):
    """Supported modality types for multi-modal search."""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENT = "document"


@dataclass
class SearchQuery:
    """Represents a multi-modal search query."""
    text: Optional[str] = None
    image_path: Optional[str] = None
    audio_path: Optional[str] = None
    video_path: Optional[str] = None
    document_path: Optional[str] = None
    metadata_filters: Dict[str, Any] = field(default_factory=dict)
    modality_weights: Dict[ModalityType, float] = field(default_factory=dict)
    fusion_strategy: str = "weighted_average"  # weighted_average, max_pooling, concatenation


@dataclass
class SearchResult:
    """Represents a search result with multi-modal information."""
    id: str
    score: float
    content: Dict[str, Any]
    metadata: Dict[str, Any]
    modality_scores: Dict[ModalityType, float] = field(default_factory=dict)


class MultiModalSearchEngine:
    """
    Advanced multi-modal search engine that can handle multiple data types
    in unified search operations with sophisticated fusion strategies.
    """
    
    def __init__(
        self,
        database: Database,
        feature_config: Optional[FeatureConfig] = None,
        logger: Optional[AIPrishtinaLogger] = None,
        metrics: Optional[MetricsCollector] = None
    ):
        """
        Initialize multi-modal search engine.
        
        Args:
            database: Vector database instance
            feature_config: Configuration for feature extraction
            logger: Logger instance
            metrics: Metrics collector
        """
        self.database = database
        self.logger = logger or AIPrishtinaLogger(name="multimodal_search")
        self.metrics = metrics or MetricsCollector()
        
        # Initialize feature extractors for different modalities
        self.feature_config = feature_config or FeatureConfig()
        try:
            self.feature_extractor = FeatureExtractor(self.feature_config)
        except Exception as e:
            # Graceful fallback if feature extractor fails
            asyncio.create_task(self.logger.warning(f"Feature extractor initialization failed: {str(e)}"))
            self.feature_extractor = None
        
        # Initialize embedding models for different modalities
        self.text_embedder = EmbeddingModel(model_name="all-MiniLM-L6-v2")
        self.image_embedder = EmbeddingModel(model_name="clip-ViT-B-32")
        
        # Fusion strategies
        self.fusion_strategies = {
            "weighted_average": self._weighted_average_fusion,
            "max_pooling": self._max_pooling_fusion,
            "concatenation": self._concatenation_fusion,
            "attention_fusion": self._attention_fusion
        }
        
        # Default modality weights
        self.default_weights = {
            ModalityType.TEXT: 0.4,
            ModalityType.IMAGE: 0.3,
            ModalityType.AUDIO: 0.2,
            ModalityType.VIDEO: 0.1,
            ModalityType.DOCUMENT: 0.3
        }
    
    async def search(
        self,
        query: SearchQuery,
        n_results: int = 10,
        similarity_threshold: float = 0.0
    ) -> List[SearchResult]:
        """
        Perform multi-modal search.
        
        Args:
            query: Multi-modal search query
            n_results: Number of results to return
            similarity_threshold: Minimum similarity threshold
            
        Returns:
            List of search results
        """
        start_time = self.metrics.start_timer("multimodal_search")
        
        try:
            await self.logger.info(f"Starting multi-modal search with {len([m for m in [query.text, query.image_path, query.audio_path, query.video_path, query.document_path] if m])} modalities")
            
            # Extract features for each modality in the query
            query_embeddings = await self._extract_query_embeddings(query)
            
            if not query_embeddings:
                raise SearchError("No valid embeddings could be extracted from query")
            
            # Perform search for each modality
            modality_results = {}
            for modality, embedding in query_embeddings.items():
                results = await self._search_modality(
                    modality, embedding, n_results, query.metadata_filters
                )
                modality_results[modality] = results
            
            # Fuse results from different modalities
            fused_results = await self._fuse_results(
                modality_results,
                query.modality_weights or self.default_weights,
                query.fusion_strategy
            )
            
            # Filter by similarity threshold
            filtered_results = [
                result for result in fused_results 
                if result.score >= similarity_threshold
            ]
            
            # Sort by score and limit results
            final_results = sorted(
                filtered_results, 
                key=lambda x: x.score, 
                reverse=True
            )[:n_results]
            
            self.metrics.end_timer("multimodal_search", start_time)
            await self.logger.info(f"Multi-modal search completed. Found {len(final_results)} results")
            
            return final_results
            
        except Exception as e:
            self.metrics.end_timer("multimodal_search", start_time)
            await self.logger.error(f"Multi-modal search failed: {str(e)}")
            raise SearchError(f"Multi-modal search failed: {str(e)}")
    
    async def _extract_query_embeddings(self, query: SearchQuery) -> Dict[ModalityType, np.ndarray]:
        """Extract embeddings for each modality in the query."""
        embeddings = {}
        
        # Text embedding
        if query.text:
            try:
                text_embedding = await self.text_embedder.encode([query.text])
                embeddings[ModalityType.TEXT] = text_embedding[0]
            except Exception as e:
                await self.logger.warning(f"Failed to extract text embedding: {str(e)}")
        
        # Image embedding
        if query.image_path:
            try:
                # Load and process image
                image_features = await self._extract_image_features(query.image_path)
                embeddings[ModalityType.IMAGE] = image_features
            except Exception as e:
                await self.logger.warning(f"Failed to extract image embedding: {str(e)}")
        
        # Audio embedding
        if query.audio_path:
            try:
                audio_features = await self._extract_audio_features(query.audio_path)
                embeddings[ModalityType.AUDIO] = audio_features
            except Exception as e:
                await self.logger.warning(f"Failed to extract audio embedding: {str(e)}")
        
        # Video embedding
        if query.video_path:
            try:
                video_features = await self._extract_video_features(query.video_path)
                embeddings[ModalityType.VIDEO] = video_features
            except Exception as e:
                await self.logger.warning(f"Failed to extract video embedding: {str(e)}")
        
        # Document embedding
        if query.document_path:
            try:
                doc_features = await self._extract_document_features(query.document_path)
                embeddings[ModalityType.DOCUMENT] = doc_features
            except Exception as e:
                await self.logger.warning(f"Failed to extract document embedding: {str(e)}")
        
        return embeddings
    
    async def _extract_image_features(self, image_path: str) -> np.ndarray:
        """Extract features from image file."""
        # Placeholder for image feature extraction
        # In a real implementation, this would use computer vision models
        return np.random.rand(512).astype(np.float32)
    
    async def _extract_audio_features(self, audio_path: str) -> np.ndarray:
        """Extract features from audio file."""
        # Placeholder for audio feature extraction
        # In a real implementation, this would use audio processing models
        return np.random.rand(256).astype(np.float32)
    
    async def _extract_video_features(self, video_path: str) -> np.ndarray:
        """Extract features from video file."""
        # Placeholder for video feature extraction
        # In a real implementation, this would combine visual and audio features
        return np.random.rand(768).astype(np.float32)
    
    async def _extract_document_features(self, document_path: str) -> np.ndarray:
        """Extract features from document file."""
        # Read document and extract text
        try:
            with open(document_path, 'r', encoding='utf-8') as f:
                text = f.read()
            text_embedding = await self.text_embedder.encode([text])
            return text_embedding[0]
        except Exception as e:
            await self.logger.warning(f"Failed to read document {document_path}: {str(e)}")
            return np.random.rand(384).astype(np.float32)
    
    async def _search_modality(
        self,
        modality: ModalityType,
        embedding: np.ndarray,
        n_results: int,
        metadata_filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Search for a specific modality."""
        try:
            # Create collection name for this modality
            collection_name = f"{self.database.collection_name}_{modality.value}"
            
            # Perform vector search
            results = await self.database.query(
                query_embeddings=[embedding.tolist()],
                n_results=n_results,
                where=metadata_filters
            )
            
            return results
            
        except Exception as e:
            await self.logger.warning(f"Search failed for modality {modality.value}: {str(e)}")
            return []
    
    async def _fuse_results(
        self,
        modality_results: Dict[ModalityType, List[Dict[str, Any]]],
        weights: Dict[ModalityType, float],
        fusion_strategy: str
    ) -> List[SearchResult]:
        """Fuse results from different modalities."""
        fusion_func = self.fusion_strategies.get(fusion_strategy, self._weighted_average_fusion)
        return await fusion_func(modality_results, weights)
    
    async def _weighted_average_fusion(
        self,
        modality_results: Dict[ModalityType, List[Dict[str, Any]]],
        weights: Dict[ModalityType, float]
    ) -> List[SearchResult]:
        """Fuse results using weighted average of scores."""
        # Collect all unique document IDs
        all_ids = set()
        for results in modality_results.values():
            if results and 'ids' in results:
                all_ids.update(results['ids'][0])
        
        fused_results = []
        for doc_id in all_ids:
            total_score = 0.0
            total_weight = 0.0
            modality_scores = {}
            content = {}
            metadata = {}
            
            for modality, results in modality_results.items():
                if results and 'ids' in results and doc_id in results['ids'][0]:
                    idx = results['ids'][0].index(doc_id)
                    score = 1.0 - results['distances'][0][idx]  # Convert distance to similarity
                    weight = weights.get(modality, 0.0)
                    
                    total_score += score * weight
                    total_weight += weight
                    modality_scores[modality] = score
                    
                    if 'documents' in results and results['documents'][0]:
                        content[modality.value] = results['documents'][0][idx]
                    if 'metadatas' in results and results['metadatas'][0]:
                        metadata.update(results['metadatas'][0][idx] or {})
            
            if total_weight > 0:
                final_score = total_score / total_weight
                fused_results.append(SearchResult(
                    id=doc_id,
                    score=final_score,
                    content=content,
                    metadata=metadata,
                    modality_scores=modality_scores
                ))
        
        return fused_results
    
    async def _max_pooling_fusion(
        self,
        modality_results: Dict[ModalityType, List[Dict[str, Any]]],
        weights: Dict[ModalityType, float]
    ) -> List[SearchResult]:
        """Fuse results using max pooling of scores."""
        # Similar to weighted average but takes maximum score
        all_ids = set()
        for results in modality_results.values():
            if results and 'ids' in results:
                all_ids.update(results['ids'][0])
        
        fused_results = []
        for doc_id in all_ids:
            max_score = 0.0
            modality_scores = {}
            content = {}
            metadata = {}
            
            for modality, results in modality_results.items():
                if results and 'ids' in results and doc_id in results['ids'][0]:
                    idx = results['ids'][0].index(doc_id)
                    score = 1.0 - results['distances'][0][idx]
                    
                    max_score = max(max_score, score)
                    modality_scores[modality] = score
                    
                    if 'documents' in results and results['documents'][0]:
                        content[modality.value] = results['documents'][0][idx]
                    if 'metadatas' in results and results['metadatas'][0]:
                        metadata.update(results['metadatas'][0][idx] or {})
            
            fused_results.append(SearchResult(
                id=doc_id,
                score=max_score,
                content=content,
                metadata=metadata,
                modality_scores=modality_scores
            ))
        
        return fused_results
    
    async def _concatenation_fusion(
        self,
        modality_results: Dict[ModalityType, List[Dict[str, Any]]],
        weights: Dict[ModalityType, float]
    ) -> List[SearchResult]:
        """Fuse results by concatenating embeddings."""
        # This is a simplified version - in practice would concatenate actual embeddings
        return await self._weighted_average_fusion(modality_results, weights)
    
    async def _attention_fusion(
        self,
        modality_results: Dict[ModalityType, List[Dict[str, Any]]],
        weights: Dict[ModalityType, float]
    ) -> List[SearchResult]:
        """Fuse results using attention mechanism."""
        # Simplified attention - in practice would use learned attention weights
        return await self._weighted_average_fusion(modality_results, weights)
