"""
Additional features for Chroma vectorization and data processing.
"""

from typing import List, Dict, Any, Optional, Union, Tuple
import numpy as np
from dataclasses import dataclass
import chromadb
from chromadb.utils import embedding_functions
from chromadb.api.types import (
    Documents,
    Embeddings,
    Metadatas,
    Where,
    WhereDocument,
    QueryResult
)
from .exceptions import FeatureError
from .logger import AIPrishtinaLogger
import asyncio
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
import cv2
import soundfile as sf
from sentence_transformers import SentenceTransformer

@dataclass
class FeatureConfig:
    """Configuration for feature extraction."""
    
    normalize: bool = True
    dimensionality_reduction: Optional[str] = None
    feature_scaling: bool = True
    cache_features: bool = True
    batch_size: int = 100
    device: str = "cpu"
    collection_name: str = "features"
    collection_metadata: Optional[Dict[str, Any]] = None
    hnsw_config: Optional[Dict[str, Any]] = None
    distance_function: str = "cosine"
    embedding_function: str = "all-MiniLM-L6-v2"
    metadata: Optional[Dict[str, Any]] = None
    persist_directory: str = ".chroma"

class FeatureExtractor:
    """Extracts features from various data types."""
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: str = "cpu",
        logger: Optional[AIPrishtinaLogger] = None
    ):
        """Initialize feature extractor.
        
        Args:
            model_name: Name of the model to use
            device: Device to use for model inference
            logger: Optional logger instance
        """
        self.model_name = model_name
        self.device = device
        self.logger = logger or AIPrishtinaLogger()
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._init_model()
        
    def _init_model(self) -> None:
        """Initialize the feature extraction model."""
        try:
            import sentence_transformers
            self.model = sentence_transformers.SentenceTransformer(
                self.model_name,
                device=self.device
            )
            asyncio.create_task(self.logger.info(f"Initialized feature extractor with model: {self.model_name}"))
        except Exception as e:
            asyncio.create_task(self.logger.error(f"Failed to initialize feature extractor: {str(e)}"))
            raise FeatureExtractionError(f"Failed to initialize feature extractor: {str(e)}")
            
    async def extract_text_features(
        self,
        texts: List[str],
        batch_size: int = 32,
        **kwargs
    ) -> np.ndarray:
        """Extract features from text.
        
        Args:
            texts: List of text strings
            batch_size: Batch size for processing
            **kwargs: Additional parameters for the model
            
        Returns:
            Array of text features
        """
        try:
            loop = asyncio.get_event_loop()
            features = await loop.run_in_executor(
                self._executor,
                lambda: self.model.encode(texts, batch_size=batch_size, **kwargs)
            )
            await self.logger.debug(f"Extracted features from {len(texts)} texts")
            return features
        except Exception as e:
            raise FeatureExtractionError(f"Failed to extract text features: {str(e)}")
            
    async def extract_image_features(
        self,
        images: List[Union[str, np.ndarray, Image.Image]],
        batch_size: int = 32,
        **kwargs
    ) -> np.ndarray:
        """Extract features from images.
        
        Args:
            images: List of images (file paths, numpy arrays, or PIL Images)
            batch_size: Batch size for processing
            **kwargs: Additional parameters for the model
            
        Returns:
            Array of image features
        """
        try:
            # Convert images to PIL Images
            pil_images = []
            for img in images:
                if isinstance(img, str):
                    pil_images.append(Image.open(img))
                elif isinstance(img, np.ndarray):
                    pil_images.append(Image.fromarray(img))
                elif isinstance(img, Image.Image):
                    pil_images.append(img)
                else:
                    raise ValueError(f"Unsupported image type: {type(img)}")
                    
            # Extract features
            loop = asyncio.get_event_loop()
            features = await loop.run_in_executor(
                self._executor,
                lambda: self.model.encode(pil_images, batch_size=batch_size, **kwargs)
            )
            await self.logger.debug(f"Extracted features from {len(images)} images")
            return features
        except Exception as e:
            raise FeatureExtractionError(f"Failed to extract image features: {str(e)}")
            
    async def extract_audio_features(
        self,
        audio_files: List[str],
        batch_size: int = 32,
        **kwargs
    ) -> np.ndarray:
        """Extract features from audio files.
        
        Args:
            audio_files: List of audio file paths
            batch_size: Batch size for processing
            **kwargs: Additional parameters for the model
            
        Returns:
            Array of audio features
        """
        try:
            # Load audio files
            audio_data = []
            for file in audio_files:
                data, _ = sf.read(file)
                audio_data.append(data)
                
            # Extract features
            loop = asyncio.get_event_loop()
            features = await loop.run_in_executor(
                self._executor,
                lambda: self.model.encode(audio_data, batch_size=batch_size, **kwargs)
            )
            await self.logger.debug(f"Extracted features from {len(audio_files)} audio files")
            return features
        except Exception as e:
            raise FeatureExtractionError(f"Failed to extract audio features: {str(e)}")
            
    async def extract_video_features(
        self,
        video_files: List[str],
        batch_size: int = 32,
        **kwargs
    ) -> np.ndarray:
        """Extract features from video files.
        
        Args:
            video_files: List of video file paths
            batch_size: Batch size for processing
            **kwargs: Additional parameters for the model
            
        Returns:
            Array of video features
        """
        try:
            # Extract frames from videos
            frames = []
            for file in video_files:
                cap = cv2.VideoCapture(file)
                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break
                    frames.append(frame)
                cap.release()
                
            # Extract features
            loop = asyncio.get_event_loop()
            features = await loop.run_in_executor(
                self._executor,
                lambda: self.model.encode(frames, batch_size=batch_size, **kwargs)
            )
            await self.logger.debug(f"Extracted features from {len(video_files)} videos")
            return features
        except Exception as e:
            raise FeatureExtractionError(f"Failed to extract video features: {str(e)}")
            
    async def extract_mixed_features(
        self,
        data: List[Dict[str, Any]],
        batch_size: int = 32,
        **kwargs
    ) -> Dict[str, np.ndarray]:
        """Extract features from mixed data types.
        
        Args:
            data: List of dictionaries containing different data types
            batch_size: Batch size for processing
            **kwargs: Additional parameters for the model
            
        Returns:
            Dictionary of feature arrays by type
        """
        try:
            features = {}
            
            # Group data by type
            text_data = []
            image_data = []
            audio_data = []
            video_data = []
            
            for item in data:
                if "text" in item:
                    text_data.append(item["text"])
                if "image" in item:
                    image_data.append(item["image"])
                if "audio" in item:
                    audio_data.append(item["audio"])
                if "video" in item:
                    video_data.append(item["video"])
                    
            # Extract features for each type
            if text_data:
                features["text"] = await self.extract_text_features(text_data, batch_size, **kwargs)
            if image_data:
                features["image"] = await self.extract_image_features(image_data, batch_size, **kwargs)
            if audio_data:
                features["audio"] = await self.extract_audio_features(audio_data, batch_size, **kwargs)
            if video_data:
                features["video"] = await self.extract_video_features(video_data, batch_size, **kwargs)
                
            await self.logger.debug(f"Extracted mixed features from {len(data)} items")
            return features
        except Exception as e:
            raise FeatureExtractionError(f"Failed to extract mixed features: {str(e)}")
            
    async def normalize_features(self, features: np.ndarray) -> np.ndarray:
        """Normalize features to unit length.
        
        Args:
            features: Input features
            
        Returns:
            Normalized features
        """
        try:
            loop = asyncio.get_event_loop()
            normalized = await loop.run_in_executor(
                self._executor,
                lambda: features / np.linalg.norm(features, axis=1, keepdims=True)
            )
            return normalized
        except Exception as e:
            raise FeatureExtractionError(f"Failed to normalize features: {str(e)}")
            
    def __del__(self):
        """Cleanup executor on deletion."""
        if hasattr(self, '_executor'):
            self._executor.shutdown(wait=False)

class TextFeatureExtractor(FeatureExtractor):
    """Extract features from text data."""

    def __init__(self, config: FeatureConfig):
        """Initialize text feature extractor.

        Args:
            config: Feature configuration
        """
        super().__init__(config.embedding_function, config.device)
        self.config = config
        self.model = SentenceTransformer(config.embedding_function)
        self.logger = AIPrishtinaLogger(__name__)
        self.logger.info(f"Initialized feature extractor with model: {config.embedding_function}")

    async def extract_text(self, text: str) -> np.ndarray:
        """Extract features from a single text.

        Args:
            text: Input text

        Returns:
            Feature vector as numpy array
        """
        try:
            # Encode text using sentence transformer
            embedding = self.model.encode(text)
            
            # Normalize if configured
            if self.config.normalize:
                embedding = self._normalize_vectors(embedding)
            
            return embedding
        except Exception as e:
            self.logger.error(f"Failed to extract text features: {str(e)}")
            raise FeatureError(f"Text feature extraction failed: {str(e)}")

    async def extract_text_batch(self, texts: List[str]) -> np.ndarray:
        """Extract features from a batch of texts.

        Args:
            texts: List of input texts

        Returns:
            Feature vectors as numpy array
        """
        try:
            # Encode texts using sentence transformer
            embeddings = self.model.encode(texts)
            
            # Normalize if configured
            if self.config.normalize:
                embeddings = self._normalize_vectors(embeddings)
            
            return embeddings
        except Exception as e:
            self.logger.error(f"Failed to extract batch text features: {str(e)}")
            raise FeatureError(f"Batch text feature extraction failed: {str(e)}")

    def _normalize_vectors(self, vectors: np.ndarray) -> np.ndarray:
        """Normalize vectors to unit length.

        Args:
            vectors: Input vectors

        Returns:
            Normalized vectors
        """
        try:
            # Handle single vector
            if len(vectors.shape) == 1:
                norm = np.linalg.norm(vectors)
                if norm > 0:
                    return vectors / norm
                return vectors

            # Handle batch of vectors
            norms = np.linalg.norm(vectors, axis=1, keepdims=True)
            return np.divide(vectors, norms, where=(norms > 0))
        except Exception as e:
            self.logger.error(f"Failed to normalize vectors: {str(e)}")
            raise FeatureError(f"Vector normalization failed: {str(e)}")

    def _extract_embedding(self, text: str) -> List[float]:
        """Extract text embedding using Chroma's embedding function."""
        try:
            embedding = self.embedding_fn([text])[0]
            return embedding
        except Exception as e:
            print(f"Failed to extract embedding: {str(e)}")
            return [0.0] * 1536  # Default embedding size

    def _extract_length(self, text: str) -> float:
        """Extract text length feature."""
        return float(len(text))

    def _extract_complexity(self, text: str) -> float:
        """Extract text complexity feature."""
        words = text.split()
        if not words:
            return 0.0
        return float(sum(len(word) for word in words) / len(words))

    def _normalize_features(self, features: np.ndarray) -> np.ndarray:
        """Normalize features to [0, 1] range."""
        if len(features) == 0:
            return features
        min_val = features.min()
        max_val = features.max()
        if max_val == min_val:
            return np.zeros_like(features)
        return (features - min_val) / (max_val - min_val)

class ImageFeatureExtractor(FeatureExtractor):
    """Extract features from image data."""
    
    def __init__(self, config: FeatureConfig):
        super().__init__(config.embedding_function, config.device)
        self._image_features = {
            'color': self._extract_color,
            'texture': self._extract_texture,
            'shape': self._extract_shape,
            'edges': self._extract_edges
        }
    
    def extract(self, image: Any) -> np.ndarray:
        """Extract features from image."""
        if self.config.cache_features and id(image) in self._feature_cache:
            return self._feature_cache[id(image)]
        
        features = []
        for feature_name, extractor in self._image_features.items():
            try:
                feature_value = extractor(image)
                features.append(feature_value)
            except Exception as e:
                print(f"Failed to extract {feature_name}: {str(e)}")
                features.append(0.0)
        
        features = np.array(features)
        if self.config.normalize:
            features = self._normalize_features(features)
        
        if self.config.cache_features:
            self._feature_cache[id(image)] = features
        
        return features
    
    @staticmethod
    def _extract_color(image: Any) -> np.ndarray:
        """Extract color features."""
        # Placeholder for color feature extraction
        return np.zeros(3)

    @staticmethod
    def _extract_texture(self, image: Any) -> np.ndarray:
        """Extract texture features."""
        # Placeholder for texture feature extraction
        return np.zeros(3)

    @staticmethod
    def _extract_shape(self, image: Any) -> np.ndarray:
        """Extract shape features."""
        # Placeholder for shape feature extraction
        return np.zeros(3)

    @staticmethod
    def _extract_edges(self, image: Any) -> np.ndarray:
        """Extract edge features."""
        # Placeholder for edge feature extraction
        return np.zeros(3)

    @staticmethod
    def _normalize_features(self, features: np.ndarray) -> np.ndarray:
        """Normalize features to [0, 1] range."""
        if len(features) == 0:
            return features
        return (features - features.min()) / (features.max() - features.min())

class AudioFeatureExtractor(FeatureExtractor):
    """Extract features from audio data."""
    
    def __init__(self, config: FeatureConfig):
        super().__init__(config.embedding_function, config.device)
        self._audio_features = {
            'mfcc': self._extract_mfcc,
            'spectral': self._extract_spectral,
            'temporal': self._extract_temporal,
            'rhythm': self._extract_rhythm
        }
    
    def extract(self, audio: Any) -> np.ndarray:
        """Extract features from audio."""
        if self.config.cache_features and id(audio) in self._feature_cache:
            return self._feature_cache[id(audio)]
        
        features = []
        for feature_name, extractor in self._audio_features.items():
            try:
                feature_value = extractor(audio)
                features.append(feature_value)
            except Exception as e:
                print(f"Failed to extract {feature_name}: {str(e)}")
                features.append(0.0)
        
        features = np.array(features)
        if self.config.normalize:
            features = self._normalize_features(features)
        
        if self.config.cache_features:
            self._feature_cache[id(audio)] = features
        
        return features

    @staticmethod
    def _extract_mfcc(self, audio: Any) -> np.ndarray:
        """Extract MFCC features."""
        # Placeholder for MFCC feature extraction
        return np.zeros(13)

    @staticmethod
    def _extract_spectral(self, audio: Any) -> np.ndarray:
        """Extract spectral features."""
        # Placeholder for spectral feature extraction
        return np.zeros(5)

    @staticmethod
    def _extract_temporal(self, audio: Any) -> np.ndarray:
        """Extract temporal features."""
        # Placeholder for temporal feature extraction
        return np.zeros(5)

    @staticmethod
    def _extract_rhythm(self, audio: Any) -> np.ndarray:
        """Extract rhythm features."""
        # Placeholder for rhythm feature extraction
        return np.zeros(5)

    @staticmethod
    def _normalize_features(self, features: np.ndarray) -> np.ndarray:
        """Normalize features to [0, 1] range."""
        if len(features) == 0:
            return features
        return (features - features.min()) / (features.max() - features.min())

class FeatureProcessor:
    """Process and manage feature extraction."""

    def __init__(self, config: FeatureConfig):
        """Initialize feature processor.

        Args:
            config: Feature configuration
        """
        self.config = config
        self.logger = AIPrishtinaLogger(__name__)
        self._feature_extractors = {}
        self._init_extractors()

    def _init_extractors(self):
        """Initialize default feature extractors."""
        self._feature_extractors = {
            "text": TextFeatureExtractor(self.config),
            "numerical": NumericalFeatureExtractor(self.config),
            "categorical": CategoricalFeatureExtractor(self.config)
        }

    def register_feature_extractor(self, data_type: str):
        """Register a custom feature extractor.

        Args:
            data_type: Type of data the extractor handles

        Returns:
            Decorator function
        """
        def decorator(extractor_class):
            self._feature_extractors[data_type] = extractor_class(self.config)
            return extractor_class
        return decorator

    async def process(self, data: Dict[str, Any]) -> np.ndarray:
        """Process input data and return feature vector.

        Args:
            data: Input data dictionary

        Returns:
            Feature vector as numpy array
        """
        if not data:
            raise FeatureError("Empty data provided")

        features = []
        for data_type, value in data.items():
            if data_type in self._feature_extractors:
                extractor = self._feature_extractors[data_type]
                if data_type == "text":
                    feature_vector = await extractor.extract_text(value)
                else:
                    feature_vector = await extractor.extract(value)
                features.append(feature_vector)
            else:
                raise FeatureError(f"No extractor registered for data type: {data_type}")

        # Combine features
        if not features:
            raise FeatureError("No features were extracted")
        
        # Ensure all features are 2D arrays
        features = [f.reshape(1, -1) if len(f.shape) == 1 else f for f in features]
        combined_features = np.concatenate(features, axis=1)

        # Apply feature scaling if configured
        if self.config.feature_scaling:
            combined_features = self._scale_features(combined_features)

        return combined_features

    def _scale_features(self, features: np.ndarray) -> np.ndarray:
        """Scale features to a common range.

        Args:
            features: Input features

        Returns:
            Scaled features
        """
        try:
            # Min-max scaling
            min_vals = np.min(features, axis=0)
            max_vals = np.max(features, axis=0)
            range_vals = max_vals - min_vals
            range_vals[range_vals == 0] = 1  # Avoid division by zero
            return (features - min_vals) / range_vals
        except Exception as e:
            self.logger.error(f"Failed to scale features: {str(e)}")
            raise FeatureError(f"Feature scaling failed: {str(e)}")

    async def add_to_collection(
        self,
        data: Dict[str, Any],
        id: str,
        metadata: Optional[Dict[str, Any]] = None,
        documents: Optional[List[str]] = None
    ) -> None:
        """Add features to collection.

        Args:
            data: Input data
            id: Unique identifier
            metadata: Additional metadata
            documents: Original documents
        """
        try:
            features = await self.process(data)
            if self.config.cache_features:
                # Cache features
                pass  # TODO: Implement feature caching
        except Exception as e:
            self.logger.error(f"Failed to add features to collection: {str(e)}")
            raise FeatureError(f"Failed to add features: {str(e)}")

    async def query_collection(
        self,
        query_data: Dict[str, Any],
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Query collection for similar features.

        Args:
            query_data: Query data
            n_results: Number of results to return
            where: Filter conditions

        Returns:
            List of results with metadata
        """
        try:
            query_features = await self.process(query_data)
            # TODO: Implement collection querying
            return []
        except Exception as e:
            self.logger.error(f"Failed to query collection: {str(e)}")
            raise FeatureError(f"Failed to query collection: {str(e)}")

class FeatureRegistry:
    """Registry for managing feature extractors and processors."""
    
    def __init__(self):
        self._extractors = {}
        self._processors = {}
    
    def register_extractor(self, name: str, extractor: FeatureExtractor):
        """Register a feature extractor."""
        self._extractors[name] = extractor
    
    def register_processor(self, name: str, processor: FeatureProcessor):
        """Register a feature processor."""
        self._processors[name] = processor
    
    def get_extractor(self, name: str) -> FeatureExtractor:
        """Get a registered feature extractor."""
        if name not in self._extractors:
            raise FeatureError(f"Extractor '{name}' not found")
        return self._extractors[name]
    
    def get_processor(self, name: str) -> FeatureProcessor:
        """Get a registered feature processor."""
        if name not in self._processors:
            raise FeatureError(f"Processor '{name}' not found")
        return self._processors[name]

class NumericalFeatureExtractor:
    def __init__(self, config: FeatureConfig):
        self.config = config
        self.logger = AIPrishtinaLogger(__name__)
        self.logger.info("Initialized numerical feature extractor")

    async def _normalize_vectors(self, vectors: np.ndarray) -> np.ndarray:
        """Normalize vectors to unit length.
        
        Args:
            vectors: Input vectors to normalize
            
        Returns:
            Normalized vectors
        """
        try:
            # Calculate L2 norm
            norms = np.linalg.norm(vectors, axis=1, keepdims=True)
            # Avoid division by zero
            norms[norms == 0] = 1
            # Normalize
            return vectors / norms
        except Exception as e:
            await self.logger.error(f"Failed to normalize vectors: {str(e)}")
            raise FeatureError(f"Vector normalization failed: {str(e)}")

    async def extract(self, data: np.ndarray) -> np.ndarray:
        """Extract features from numerical data.
        
        Args:
            data: Input numerical data
            
        Returns:
            Extracted features as numpy array
        """
        try:
            # Ensure data is 2D
            if data.ndim == 1:
                data = data.reshape(1, -1)
                
            # Normalize if configured
            if self.config.normalize:
                data = await self._normalize_vectors(data)
                
            return data
        except Exception as e:
            await self.logger.error(f"Failed to extract numerical features: {str(e)}")
            raise FeatureError(f"Numerical feature extraction failed: {str(e)}")

class CategoricalFeatureExtractor:
    def __init__(self, config: FeatureConfig):
        self.config = config
        self.logger = AIPrishtinaLogger(__name__)
        self.logger.info("Initialized categorical feature extractor")

    async def _normalize_vectors(self, vectors: np.ndarray) -> np.ndarray:
        """Normalize vectors to unit length.
        
        Args:
            vectors: Input vectors to normalize
            
        Returns:
            Normalized vectors
        """
        try:
            # Calculate L2 norm
            norms = np.linalg.norm(vectors, axis=1, keepdims=True)
            # Avoid division by zero
            norms[norms == 0] = 1
            # Normalize
            return vectors / norms
        except Exception as e:
            await self.logger.error(f"Failed to normalize vectors: {str(e)}")
            raise FeatureError(f"Vector normalization failed: {str(e)}")

    async def extract(self, data: List[str]) -> np.ndarray:
        """Extract features from categorical data.
        
        Args:
            data: Input categorical data
            
        Returns:
            Extracted features as numpy array
        """
        try:
            # Convert categories to one-hot encoding
            unique_categories = list(set(data))
            num_categories = len(unique_categories)
            num_samples = len(data)
            
            # Create one-hot encoding
            one_hot = np.zeros((num_samples, num_categories))
            for i, category in enumerate(data):
                category_idx = unique_categories.index(category)
                one_hot[i, category_idx] = 1
                
            # Normalize if configured
            if self.config.normalize:
                one_hot = await self._normalize_vectors(one_hot)
                
            return one_hot
        except Exception as e:
            await self.logger.error(f"Failed to extract categorical features: {str(e)}")
            raise FeatureError(f"Categorical feature extraction failed: {str(e)}") 