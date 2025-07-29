"""
Example demonstrating how to use AI Prishtina VectorDB in an application.
This example shows the complete flow from setup to usage.
"""

import os
import sys
from pathlib import Path
import logging
from typing import List, Dict, Any

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

from ai_prishtina_vectordb.config.config_manager import ConfigManager
from ai_prishtina_vectordb.config.docker_manager import DockerManager, ConfigManager
from ai_prishtina_vectordb.features import FeatureProcessor, TextFeatureExtractor
from ai_prishtina_vectordb.data_sources import DataSource, TextDataSource

class AIPrishtinaApp:
    """
    Example application using AI Prishtina VectorDB.
    This class demonstrates how to integrate the library into your application.
    """
    
    def __init__(self, config_path: str, config_type: str = "yaml"):
        """
        Initialize the application.
        
        Args:
            config_path: Path to the configuration file
            config_type: Type of configuration file ("yaml" or "ini")
        """
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        
        # Initialize configuration
        self.config_manager = ConfigManager(config_path=config_path, config_type=config_type)
        if not self.config_manager.validate_config():
            raise ValueError("Invalid configuration")
        
        # Initialize Docker manager if in Docker mode
        if os.getenv('AI_PRISHTINA_DOCKER_MODE', 'false').lower() == 'true':
            self.docker_manager = DockerManager(self.config_manager)
            self._setup_docker()
        
        # Initialize feature processor
        self.feature_processor = self._setup_feature_processor()
    
    def _setup_logging(self):
        """Set up logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def _setup_docker(self):
        """Set up Docker environment if needed."""
        try:
            self.docker_manager.setup_chroma_environment()
            self.logger.info("Docker environment set up successfully")
        except Exception as e:
            self.logger.error(f"Failed to set up Docker environment: {str(e)}")
            raise
    
    def _setup_feature_processor(self) -> FeatureProcessor:
        """Set up the feature processor with configuration."""
        chroma_settings = self.config_manager.get_chroma_settings()
        return FeatureProcessor(
            collection_name=chroma_settings['collection_name'],
            persist_directory=chroma_settings['persist_directory'],
            embedding_function=chroma_settings['embedding_function'],
            embedding_model=chroma_settings['default_embedding_model']
        )
    
    def process_text_data(self, texts: List[str], metadata: List[Dict[str, Any]] = None) -> List[str]:
        """
        Process a list of text documents.
        
        Args:
            texts: List of text documents to process
            metadata: Optional list of metadata dictionaries for each document
            
        Returns:
            List of document IDs
        """
        try:
            # Create text data source
            data_source = TextDataSource(texts, metadata)
            
            # Extract features
            extractor = TextFeatureExtractor()
            features = extractor.extract_features(data_source)
            
            # Process features and store in ChromaDB
            doc_ids = self.feature_processor.process_features(features)
            
            self.logger.info(f"Successfully processed {len(doc_ids)} documents")
            return doc_ids
            
        except Exception as e:
            self.logger.error(f"Error processing text data: {str(e)}")
            raise
    
    def search_similar_documents(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents.
        
        Args:
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of similar documents with their metadata
        """
        try:
            results = self.feature_processor.search(query, n_results=n_results)
            self.logger.info(f"Found {len(results)} similar documents")
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching documents: {str(e)}")
            raise
    
    def get_document_by_id(self, doc_id: str) -> Dict[str, Any]:
        """
        Retrieve a document by its ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document data and metadata
        """
        try:
            document = self.feature_processor.get_document(doc_id)
            return document
            
        except Exception as e:
            self.logger.error(f"Error retrieving document: {str(e)}")
            raise

def main():
    """Example usage of the AIPrishtina App."""
    # Get the configuration file path
    config_path = Path(__file__).parent / "config" / "config.yaml"
    
    try:
        # Initialize the application
        app = AIPrishtinaApp(str(config_path), "yaml")
        
        # Example documents
        documents = [
            "The quick brown fox jumps over the lazy dog.",
            "A fast orange fox leaps across a sleepy canine.",
            "Machine learning is a subset of artificial intelligence.",
            "Deep learning models can process complex data patterns.",
            "Natural language processing helps computers understand text."
        ]
        
        # Example metadata
        metadata = [
            {"source": "example1", "category": "animals"},
            {"source": "example2", "category": "animals"},
            {"source": "example3", "category": "technology"},
            {"source": "example4", "category": "technology"},
            {"source": "example5", "category": "technology"}
        ]
        
        # Process documents
        print("\nProcessing documents...")
        doc_ids = app.process_text_data(documents, metadata)
        print(f"Processed {len(doc_ids)} documents")
        
        # Search for similar documents
        print("\nSearching for similar documents...")
        query = "What is machine learning?"
        results = app.search_similar_documents(query, n_results=3)
        
        print("\nSearch results:")
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"Document: {result['document']}")
            print(f"Similarity: {result['similarity']:.4f}")
            print(f"Metadata: {result['metadata']}")
        
        # Retrieve a specific document
        print("\nRetrieving a specific document...")
        doc_id = doc_ids[0]
        document = app.get_document_by_id(doc_id)
        print(f"\nRetrieved document:")
        print(f"ID: {document['id']}")
        print(f"Content: {document['document']}")
        print(f"Metadata: {document['metadata']}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 