"""
Basic text search example using AIPrishtina VectorDB.

This example demonstrates:
1. Loading text data from different sources
2. Using different embedding models
3. Performing similarity search
4. Logging operations
"""

import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from ai_prishtina_vectordb import DataSource, Database
from ai_prishtina_vectordb.logger import AIPrishtinaLogger

# Initialize logger
logger = AIPrishtinaLogger(
    level="INFO",
    log_file="logs/basic_search.log"
)

def create_sample_data():
    """Create sample text data for demonstration."""
    logger.info("Creating sample text data")
    
    # Create sample text files
    texts = [
        "The quick brown fox jumps over the lazy dog",
        "A fast orange fox leaps over a sleepy canine",
        "The weather is beautiful today",
        "It's raining cats and dogs",
        "Machine learning is transforming industries",
        "Artificial intelligence is revolutionizing technology"
    ]
    
    # Save to text files
    data_dir = Path("data/text")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    for i, text in enumerate(texts):
        file_path = data_dir / f"sample_{i}.txt"
        with open(file_path, "w") as f:
            f.write(text)
        logger.debug(f"Created sample file: {file_path}")
    
    return data_dir

def load_data(data_dir: Path):
    """Load data using different embedding models."""
    logger.info("Loading data with different embedding models")
    
    # Initialize data sources with different models
    sources = {
        "sentence_transformer": DataSource(source_type="text"),
        "custom_model": DataSource(
            source_type="text"
        )
    }
    
    results = {}
    for name, source in sources.items():
        logger.info(f"Loading data with {name}")
        try:
            result = source.load_data(
                source=data_dir,
                metadata_columns=["source"]
            )
            results[name] = result
            logger.debug(f"Successfully loaded data with {name}")
        except Exception as e:
            logger.error(f"Error loading data with {name}", error=str(e))
    
    return results

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
    """Main function demonstrating text search functionality."""
    logger.info("Starting text search example")
    
    # Create sample data
    data_dir = create_sample_data()
    
    # Load data with different models
    results = load_data(data_dir)
    
    # Initialize database
    database = Database()
    
    # Add data to database
    for name, result in results.items():
        logger.info(f"Adding data from {name} to database")
        try:
            database.add(
                documents=result["documents"],
                metadatas=result["metadatas"],
                ids=result["ids"]
            )
            logger.debug(f"Successfully added data from {name}")
        except Exception as e:
            logger.error(f"Error adding data from {name}", error=str(e))
    
    # Perform searches
    queries = [
        "fox jumping",
        "weather conditions",
        "AI technology"
    ]
    
    for query in queries:
        logger.info(f"Processing query: {query}")
        results = perform_search(database, query)
        if results:
            logger.info("Search results:", results=results)

if __name__ == "__main__":
    main() 