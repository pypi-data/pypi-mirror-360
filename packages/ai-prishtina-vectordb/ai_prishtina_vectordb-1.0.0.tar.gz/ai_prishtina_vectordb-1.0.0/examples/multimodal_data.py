"""
Multimodal data handling example using AI Prishtina VectorDB.

This example demonstrates:
1. Loading and processing different data types (text, images, audio)
2. Using appropriate embedding models for each data type
3. Combining different data types in a single database
4. Logging operations
"""

import os
from pathlib import Path
import numpy as np
from PIL import Image
import soundfile as sf
from ai_prishtina_vectordb import DataSource, Database
from ai_prishtina_vectordb.logger import AIPrishtinaLogger

# Initialize logger
logger = AIPrishtinaLogger(
    name="multimodal_data_example",
    level="DEBUG",
    log_file="logs/multimodal_data.log",
    log_format="json"
)

def create_sample_data():
    """Create sample multimodal data for demonstration."""
    logger.info("Creating sample multimodal data")
    
    # Create data directory
    data_dir = Path("data/multimodal")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample text files
    texts = [
        "A beautiful sunset over the ocean",
        "The sound of waves crashing on the shore",
        "Birds chirping in the morning",
        "A peaceful mountain landscape"
    ]
    
    text_dir = data_dir / "text"
    text_dir.mkdir(exist_ok=True)
    
    for i, text in enumerate(texts):
        file_path = text_dir / f"sample_{i}.txt"
        with open(file_path, "w") as f:
            f.write(text)
        logger.debug(f"Created sample text file: {file_path}")
    
    # Create sample image files (simulated)
    image_dir = data_dir / "images"
    image_dir.mkdir(exist_ok=True)
    
    for i in range(4):
        # Create a simple RGB image
        img = Image.new('RGB', (100, 100), color=(i * 50, i * 50, i * 50))
        img_path = image_dir / f"sample_{i}.png"
        img.save(img_path)
        logger.debug(f"Created sample image file: {img_path}")
    
    # Create sample audio files (simulated)
    audio_dir = data_dir / "audio"
    audio_dir.mkdir(exist_ok=True)
    
    for i in range(4):
        # Create a simple sine wave
        sample_rate = 44100
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        frequency = 440 * (i + 1)
        audio_data = np.sin(2 * np.pi * frequency * t)
        
        audio_path = audio_dir / f"sample_{i}.wav"
        sf.write(audio_path, audio_data, sample_rate)
        logger.debug(f"Created sample audio file: {audio_path}")
    
    return data_dir

def load_text_data(data_dir: Path):
    """Load and process text data."""
    logger.info("Loading text data")
    
    try:
        source = DataSource(source_type="text")
        result = source.load_data(
            source=data_dir / "text",
            metadata_columns=["source", "type"]
        )
        logger.info("Successfully loaded text data")
        return result
    except Exception as e:
        logger.error("Error loading text data", error=str(e))
        return None

def load_image_data(data_dir: Path):
    """Load and process image data."""
    logger.info("Loading image data")
    
    try:
        source = DataSource(source_type="image")
        result = source.load_data(
            source=data_dir / "images",
            metadata_columns=["source", "type"]
        )
        logger.info("Successfully loaded image data")
        return result
    except Exception as e:
        logger.error("Error loading image data", error=str(e))
        return None

def load_audio_data(data_dir: Path):
    """Load and process audio data."""
    logger.info("Loading audio data")
    
    try:
        source = DataSource(source_type="audio")
        result = source.load_data(
            source=data_dir / "audio",
            metadata_columns=["source", "type"]
        )
        logger.info("Successfully loaded audio data")
        return result
    except Exception as e:
        logger.error("Error loading audio data", error=str(e))
        return None

def perform_search(database: Database, query: str, n_results: int = 3):
    """Perform similarity search."""
    logger.info(f"Performing search for query: {query}")
    
    try:
        results = database.query(
            query_texts=[query],
            n_results=n_results
        )
        logger.info(f"Found {len(results['documents'][0])} results")
        return results
    except Exception as e:
        logger.error("Error performing search", error=str(e))
        return None

def main():
    """Main function demonstrating multimodal data handling."""
    logger.info("Starting multimodal data example")
    
    # Create sample data
    data_dir = create_sample_data()
    
    # Initialize database
    database = Database()
    
    # Load different data types
    multimodal_results = {}
    
    # Load text data
    text_result = load_text_data(data_dir)
    if text_result:
        multimodal_results["text"] = text_result
    
    # Load image data
    image_result = load_image_data(data_dir)
    if image_result:
        multimodal_results["image"] = image_result
    
    # Load audio data
    audio_result = load_audio_data(data_dir)
    if audio_result:
        multimodal_results["audio"] = audio_result
    
    # Add data to database
    for data_type, result in multimodal_results.items():
        logger.info(f"Adding {data_type} data to database")
        try:
            database.add(
                documents=result["documents"],
                metadatas=result["metadatas"],
                ids=result["ids"]
            )
            logger.debug(f"Successfully added {data_type} data")
        except Exception as e:
            logger.error(f"Error adding {data_type} data", error=str(e))
    
    # Perform searches
    queries = [
        "Find content about nature and landscapes",
        "Search for peaceful scenes",
        "Look for morning sounds"
    ]
    
    for query in queries:
        logger.info(f"Processing query: {query}")
        results = perform_search(database, query)
        if results:
            logger.info("Search results:", results=results)

if __name__ == "__main__":
    main() 