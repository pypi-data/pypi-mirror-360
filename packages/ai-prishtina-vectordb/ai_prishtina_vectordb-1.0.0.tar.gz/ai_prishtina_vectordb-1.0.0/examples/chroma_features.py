"""
Example demonstrating advanced ChromaDB features.

This example shows how to use the enhanced ChromaDB features provided by
AI Prishtina VectorDB, including collection management, optimization,
backup/restore, and advanced querying.
"""

import os
from pathlib import Path
import json
from typing import Dict, Any, List
from ai_prishtina_vectordb import VectorDatabase
from ai_prishtina_vectordb.chroma_features import ChromaFeatures
from ai_prishtina_vectordb.logger import AIPrishtinaLogger

# Initialize logger
logger = AIPrishtinaLogger(
    name="chroma_features_example",
    level="DEBUG",
    log_file="logs/chroma_features.log",
    log_format="json"
)

def create_sample_data() -> List[Dict[str, Any]]:
    """Create sample data for demonstration."""
    return [
        {
            "text": "Machine learning algorithms are transforming healthcare",
            "category": "Technology",
            "source": "Research Paper",
            "date": "2024-01-15"
        },
        {
            "text": "New breakthroughs in quantum computing research",
            "category": "Science",
            "source": "Journal Article",
            "date": "2024-02-01"
        },
        {
            "text": "Sustainable energy solutions for urban areas",
            "category": "Environment",
            "source": "News Article",
            "date": "2024-02-15"
        },
        {
            "text": "AI-powered automation in manufacturing",
            "category": "Technology",
            "source": "Industry Report",
            "date": "2024-03-01"
        },
        {
            "text": "Climate change impact on coastal regions",
            "category": "Environment",
            "source": "Research Paper",
            "date": "2024-03-15"
        }
    ]

def demonstrate_collection_management(chroma_features: ChromaFeatures):
    """Demonstrate collection management features."""
    logger.info("Demonstrating collection management")
    
    # Create collection with metadata
    collection = chroma_features.create_collection_with_metadata(
        name="demo_collection",
        metadata={
            "description": "Demo collection for ChromaDB features",
            "version": "1.0",
            "created_by": "AI Prishtina"
        },
        embedding_function="all-MiniLM-L6-v2"
    )
    
    # Get collection statistics
    stats = chroma_features.get_collection_stats("demo_collection")
    logger.info("Collection statistics:", stats=stats)
    
    return collection

def demonstrate_optimization(chroma_features: ChromaFeatures):
    """Demonstrate collection optimization."""
    logger.info("Demonstrating collection optimization")
    
    # Optimize collection with custom parameters
    chroma_features.optimize_collection(
        collection_name="demo_collection",
        optimization_params={
            "hnsw_ef_construction": 300,
            "hnsw_m": 32,
            "hnsw_ef_search": 150
        }
    )
    
    # Get updated statistics
    stats = chroma_features.get_collection_stats("demo_collection")
    logger.info("Updated collection statistics:", stats=stats)

def demonstrate_backup_restore(chroma_features: ChromaFeatures):
    """Demonstrate backup and restore functionality."""
    logger.info("Demonstrating backup and restore")
    
    # Create backup
    backup_path = "./backups"
    chroma_features.backup_collection(
        collection_name="demo_collection",
        backup_path=backup_path
    )
    
    # Restore to new collection
    chroma_features.restore_collection(
        backup_path=os.path.join(backup_path, "demo_collection_backup.json"),
        collection_name="restored_collection"
    )
    
    # Verify restoration
    stats = chroma_features.get_collection_stats("restored_collection")
    logger.info("Restored collection statistics:", stats=stats)

def demonstrate_collection_merge(chroma_features: ChromaFeatures):
    """Demonstrate collection merging."""
    logger.info("Demonstrating collection merging")
    
    # Create second collection
    chroma_features.create_collection_with_metadata(
        name="second_collection",
        metadata={"description": "Second collection for merging"}
    )
    
    # Merge collections
    chroma_features.merge_collections(
        source_collection="demo_collection",
        target_collection="second_collection",
        merge_strategy="append"
    )
    
    # Verify merge
    stats = chroma_features.get_collection_stats("second_collection")
    logger.info("Merged collection statistics:", stats=stats)

def demonstrate_similarity_matrix(chroma_features: ChromaFeatures):
    """Demonstrate similarity matrix generation."""
    logger.info("Demonstrating similarity matrix")
    
    # Get similarity matrix for all documents
    matrix = chroma_features.get_similarity_matrix(
        collection_name="demo_collection",
        query_ids=["doc1", "doc2", "doc3"],
        n_results=2
    )
    
    logger.info("Similarity matrix:", matrix=matrix)

def main():
    """Main function demonstrating ChromaDB features."""
    logger.info("Starting ChromaDB features example")
    
    try:
        # Initialize ChromaDB features
        chroma_features = ChromaFeatures(
            persist_directory="./data/chroma"
        )
        
        # Create sample data
        sample_data = create_sample_data()
        
        # Initialize database
        db = VectorDatabase(
            collection_name="demo_collection",
            persist_directory="./data/chroma"
        )
        
        # Add sample data
        db.add(
            documents=[doc["text"] for doc in sample_data],
            metadatas=[{
                "category": doc["category"],
                "source": doc["source"],
                "date": doc["date"]
            } for doc in sample_data],
            ids=[f"doc{i+1}" for i in range(len(sample_data))]
        )
        
        # Demonstrate features
        demonstrate_collection_management(chroma_features)
        demonstrate_optimization(chroma_features)
        demonstrate_backup_restore(chroma_features)
        demonstrate_collection_merge(chroma_features)
        demonstrate_similarity_matrix(chroma_features)
        
        logger.info("Successfully demonstrated all ChromaDB features")
        
    except Exception as e:
        logger.error("Error in main function", error=str(e))
        raise

if __name__ == "__main__":
    main() 