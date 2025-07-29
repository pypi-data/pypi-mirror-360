"""
Embedding functionality for AIPrishtina VectorDB.
"""

import numpy as np
from typing import List, Union, Optional
from .logger import AIPrishtinaLogger
from .exceptions import EmbeddingError
import os
import asyncio
from concurrent.futures import ThreadPoolExecutor

class EmbeddingModel:
    """Model for generating embeddings."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: str = "cpu"):
        """Initialize the embedding model.
        
        Args:
            model_name: Name of the model to use
            device: Device to run the model on (cpu/cuda)
        """
        self.model_name = model_name
        self.device = device
        self.logger = AIPrishtinaLogger()
        self._init_model()

    def _init_model(self) -> None:
        """Initialize the embedding model."""
        try:
            import sentence_transformers
            from huggingface_hub import HfFolder
            import aiohttp
            from aiohttp import ClientTimeout
            from aiohttp import TCPConnector

            # Configure retry strategy
            timeout = ClientTimeout(total=30)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            connector = TCPConnector(limit=10, force_close=True, loop=loop)
            
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector
            )
            
            # Initialize model
            self.model = sentence_transformers.SentenceTransformer(
                self.model_name,
                device=self.device
            )
            
            # Get model dimensions
            self.dimensions = self.model.get_sentence_embedding_dimension()
            
        except Exception as e:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.logger.error(f"Failed to initialize embedding model: {str(e)}"))
            raise EmbeddingError(f"Failed to initialize embedding model: {str(e)}")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if hasattr(self, 'session'):
            await self.session.close()

    def __del__(self):
        """Cleanup on deletion."""
        if hasattr(self, 'session'):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.session.close())

    async def encode(self, texts: List[str], batch_size: int = 32, **kwargs) -> np.ndarray:
        """Generate embeddings for texts.
        
        Args:
            texts: List of text strings
            batch_size: Batch size for processing
            **kwargs: Additional parameters for the model
            
        Returns:
            Array of embeddings
        """
        try:
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                self._executor,
                lambda: self.model.encode(texts, batch_size=batch_size, **kwargs)
            )
            await self.logger.debug(f"Generated embeddings for {len(texts)} texts")
            return embeddings
        except Exception as e:
            raise EmbeddingError(f"Failed to generate embeddings: {str(e)}")
            
    async def embed_text(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for text.
        
        Args:
            texts: List of text strings
            
        Returns:
            Array of embeddings
        """
        return await self.encode(texts)
            
    async def embed_image(self, images: np.ndarray) -> np.ndarray:
        """Generate embeddings for images.
        
        Args:
            images: Array of images
            
        Returns:
            Array of embeddings
        """
        try:
            # Convert images to list of PIL Images
            from PIL import Image
            import torch
            from torchvision import transforms
            from torchvision.models import resnet50, ResNet50_Weights
            
            # Initialize ResNet model
            model = resnet50(weights=ResNet50_Weights.DEFAULT)
            model = torch.nn.Sequential(*list(model.children())[:-1])  # Remove last layer
            model.eval()
            
            # Define image transform
            transform = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            
            # Process images
            embeddings = []
            loop = asyncio.get_event_loop()
            
            for img in images:
                # Convert float32/float64 to uint8
                if img.dtype in [np.float32, np.float64]:
                    img = (img * 255).astype(np.uint8)
                pil_img = Image.fromarray(img)
                tensor = transform(pil_img).unsqueeze(0)
                
                # Generate embedding
                with torch.no_grad():
                    embedding = await loop.run_in_executor(
                        self._executor,
                        lambda: model(tensor).squeeze().numpy()
                    )
                embeddings.append(embedding)
            
            embeddings = np.array(embeddings)
            await self.logger.debug(f"Generated embeddings for {len(images)} images")
            return embeddings
        except Exception as e:
            raise EmbeddingError(f"Failed to generate image embeddings: {str(e)}")
            
    async def embed_audio(self, audio: np.ndarray) -> np.ndarray:
        """Generate embeddings for audio.
        
        Args:
            audio: Array of audio data
            
        Returns:
            Array of embeddings
        """
        try:
            # Convert audio to text descriptions for now
            # In a real implementation, you would use a proper audio embedding model
            audio_descriptions = [f"Audio sample {i}" for i in range(len(audio))]
            embeddings = await self.encode(audio_descriptions)
            await self.logger.debug(f"Generated embeddings for {len(audio)} audio samples")
            return embeddings
        except Exception as e:
            raise EmbeddingError(f"Failed to generate audio embeddings: {str(e)}")
            
    async def embed_video(self, video: np.ndarray) -> np.ndarray:
        """Generate embeddings for video.
        
        Args:
            video: Array of video frames
            
        Returns:
            Array of embeddings
        """
        try:
            # Convert video frames to list of PIL Images
            from PIL import Image
            import torch
            from torchvision import transforms
            from torchvision.models import resnet50, ResNet50_Weights
            
            # Initialize ResNet model
            model = resnet50(weights=ResNet50_Weights.DEFAULT)
            model = torch.nn.Sequential(*list(model.children())[:-1])  # Remove last layer
            model.eval()
            
            # Define image transform
            transform = transforms.Compose([
                transforms.Resize(256),
                transforms.CenterCrop(224),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            
            # Process video frames
            embeddings = []
            loop = asyncio.get_event_loop()
            
            for v in video:
                frame_embeddings = []
                for frame in v:
                    # Convert float32/float64 to uint8
                    if frame.dtype in [np.float32, np.float64]:
                        frame = (frame * 255).astype(np.uint8)
                    pil_img = Image.fromarray(frame)
                    tensor = transform(pil_img).unsqueeze(0)
                    
                    # Generate embedding
                    with torch.no_grad():
                        embedding = await loop.run_in_executor(
                            self._executor,
                            lambda: model(tensor).squeeze().numpy()
                        )
                    frame_embeddings.append(embedding)
                
                # Average frame embeddings
                video_embedding = np.mean(frame_embeddings, axis=0)
                embeddings.append(video_embedding)
            
            embeddings = np.array(embeddings)
            await self.logger.debug(f"Generated embeddings for {len(video)} videos")
            return embeddings
        except Exception as e:
            raise EmbeddingError(f"Failed to generate video embeddings: {str(e)}")
            
    async def normalize_embeddings(self, embeddings: np.ndarray) -> np.ndarray:
        """Normalize embeddings to unit length.
        
        Args:
            embeddings: Input embeddings
            
        Returns:
            Normalized embeddings
        """
        try:
            loop = asyncio.get_event_loop()
            normalized = await loop.run_in_executor(
                self._executor,
                lambda: embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
            )
            return normalized
        except Exception as e:
            raise EmbeddingError(f"Failed to normalize embeddings: {str(e)}")
            
    def get_embedding_dimension(self) -> int:
        """Get the dimension of the embeddings.
        
        Returns:
            Embedding dimension
        """
        try:
            return self.model.get_sentence_embedding_dimension()
        except Exception as e:
            raise EmbeddingError(f"Failed to get embedding dimension: {str(e)}") 