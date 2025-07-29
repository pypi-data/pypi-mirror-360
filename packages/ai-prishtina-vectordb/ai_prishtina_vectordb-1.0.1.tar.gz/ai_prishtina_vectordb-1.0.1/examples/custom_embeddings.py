"""
Custom embeddings example using AI Prishtina VectorDB.

This example demonstrates:
1. Using different embedding models (Sentence Transformers, OpenAI, Custom)
2. Comparing embedding performance
3. Fine-tuning embedding parameters
4. Logging operations
"""

import os
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
from ai_prishtina_vectordb import DataSource, Database
from ai_prishtina_vectordb.logger import AIPrishtinaLogger

# Initialize logger
logger = AIPrishtinaLogger(
    name="custom_embeddings_example",
    level="DEBUG",
    log_file="logs/custom_embeddings.log",
    log_format="json"
)

def create_sample_data():
    """Create sample text data for demonstration."""
    logger.info("Creating sample text data")
    
    # Create data directory
    data_dir = Path("data/embeddings")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample text files with different topics
    texts = [
        # Technology
        "Artificial intelligence is transforming industries worldwide",
        "Machine learning models are becoming more sophisticated",
        "Deep learning has revolutionized computer vision",
        
        # Science
        "Quantum computing promises unprecedented computational power",
        "Gene editing technology is advancing rapidly",
        "Climate change research shows concerning trends",
        
        # Business
        "Digital transformation is essential for modern businesses",
        "Blockchain technology is disrupting traditional finance",
        "Data analytics drives informed decision-making"
    ]
    
    for i, text in enumerate(texts):
        file_path = data_dir / f"sample_{i}.txt"
        with open(file_path, "w") as f:
            f.write(text)
        logger.debug(f"Created sample file: {file_path}")
    
    return data_dir

def load_with_sentence_transformer(data_dir: Path):
    """Load data using Sentence Transformer model."""
    logger.info("Loading data with Sentence Transformer")
    
    try:
        source = DataSource(
            source_type="text",
            embedding_function="all-MiniLM-L6-v2"
        )
        result = source.load_data(
            source=data_dir,
            metadata_columns=["source", "model"]
        )
        logger.info("Successfully loaded data with Sentence Transformer")
        return result
    except Exception as e:
        logger.error("Error loading data with Sentence Transformer", error=str(e))
        return None

def load_with_openai(data_dir: Path):
    """Load data using OpenAI embeddings."""
    logger.info("Loading data with OpenAI embeddings")
    
    try:
        source = DataSource(
            source_type="text",
            embedding_function="text-embedding-ada-002"
        )
        result = source.load_data(
            source=data_dir,
            metadata_columns=["source", "model"]
        )
        logger.info("Successfully loaded data with OpenAI")
        return result
    except Exception as e:
        logger.error("Error loading data with OpenAI", error=str(e))
        return None

def load_with_custom_model(data_dir: Path):
    """Load data using a custom embedding model."""
    logger.info("Loading data with custom model")
    
    try:
        # Initialize custom model
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        def custom_embedding_function(texts):
            return model.encode(texts)
        
        source = DataSource(
            source_type="text",
            embedding_function=custom_embedding_function
        )
        result = source.load_data(
            source=data_dir,
            metadata_columns=["source", "model"]
        )
        logger.info("Successfully loaded data with custom model")
        return result
    except Exception as e:
        logger.error("Error loading data with custom model", error=str(e))
        return None

def compare_embeddings(database: Database, query: str, n_results: int = 3):
    """Compare search results from different embedding models."""
    logger.info(f"Comparing embeddings for query: {query}")
    
    try:
        results = database.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Analyze results
        for i, (doc, metadata) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
            logger.info(f"Result {i+1}:", {
                "document": doc,
                "model": metadata.get("model"),
                "similarity": results["distances"][0][i] if "distances" in results else None
            })
        
        return results
    except Exception as e:
        logger.error("Error comparing embeddings", error=str(e))
        return None

def main():
    """Main function demonstrating custom embeddings."""
    logger.info("Starting custom embeddings example")
    
    # Create sample data
    data_dir = create_sample_data()
    
    # Initialize database
    database = Database()
    
    # Load data with different models
    embedding_results = {}
    
    # Load with Sentence Transformer
    st_result = load_with_sentence_transformer(data_dir)
    if st_result:
        embedding_results["sentence_transformer"] = st_result
    
    # Load with OpenAI
    openai_result = load_with_openai(data_dir)
    if openai_result:
        embedding_results["openai"] = openai_result
    
    # Load with custom model
    custom_result = load_with_custom_model(data_dir)
    if custom_result:
        embedding_results["custom"] = custom_result
    
    # Add data to database
    for model_name, result in embedding_results.items():
        logger.info(f"Adding data from {model_name} to database")
        try:
            database.add(
                documents=result["documents"],
                metadatas=result["metadatas"],
                ids=result["ids"]
            )
            logger.debug(f"Successfully added data from {model_name}")
        except Exception as e:
            logger.error(f"Error adding data from {model_name}", error=str(e))
    
    # Compare embeddings with different queries
    queries = [
        "How is AI changing technology?",
        "What are the latest scientific developments?",
        "How are businesses adapting to digital transformation?"
    ]
    
    for query in queries:
        logger.info(f"Processing query: {query}")
        results = compare_embeddings(database, query)
        if results:
            logger.info("Comparison results:", results=results)

if __name__ == "__main__":
    main() 