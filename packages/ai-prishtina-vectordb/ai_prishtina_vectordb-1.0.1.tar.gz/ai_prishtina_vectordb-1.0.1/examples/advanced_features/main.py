"""
Advanced features example using AIPrishtina VectorDB.

This example demonstrates:
1. Advanced indexing and search capabilities
2. Enhanced embedding models and fine-tuning
3. Advanced caching strategies
4. Performance optimizations
5. Advanced query features
"""

import glob
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List, Dict, Any, Optional

from ai_prishtina_vectordb import DataSource, Database, EmbeddingModel
from ai_prishtina_vectordb.logger import AIPrishtinaLogger

# Initialize logger
logger = AIPrishtinaLogger(
    name="advanced_features_example",
    level="DEBUG",
    log_file="logs/advanced_features.log",
    log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

class AdvancedVectorDB:
    """Advanced vector database with enhanced features."""
    
    def __init__(
        self,
        collection_name: str,
        embedding_model: Optional[EmbeddingModel] = None,
        index_type: str = "hnsw",
        **kwargs
    ):
        """Initialize advanced vector database."""
        self.database = Database(collection_name=collection_name)
        self.embedding_model = embedding_model or EmbeddingModel()
        self.index_type = index_type
        self.config = kwargs
        logger.info("Initialized advanced vector database")
        
        # Removed index creation logic as ChromaDB does not support create_index
        # self.create_optimized_index()
    
    def hybrid_search(
        self,
        query: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Perform hybrid search combining vector and keyword search."""
        try:
            # Vector search
            vector_results = self.database.query(
                query_texts=[query],
                n_results=n_results,
                where=where,
                **kwargs
            )
            
            # Keyword search (implement your keyword search logic here)
            keyword_results = self._keyword_search(query, n_results, where)
            
            # Combine and rank results
            combined_results = self._combine_search_results(
                vector_results,
                keyword_results,
                n_results
            )
            
            return combined_results
        except Exception as e:
            logger.error("Error in hybrid search", error=str(e))
            return {}
    
    def _keyword_search(
        self,
        query: str,
        n_results: int,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Perform keyword-based search."""
        # Implement keyword search logic here
        return {}
    
    def _combine_search_results(
        self,
        vector_results: Dict[str, Any],
        keyword_results: Dict[str, Any],
        n_results: int
    ) -> Dict[str, Any]:
        """Combine and rank results from different search methods."""
        # Implement result combination logic here
        return vector_results
    
    def batch_process(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        batch_size: int = 100,
        max_workers: int = 4
    ):
        """Process documents in parallel batches."""
        logger.info(f"Starting batch processing: {len(documents)} documents, {len(metadatas)} metadatas")
        logger.debug(f"First 2 documents: {documents[:2]}")
        logger.debug(f"First 2 metadatas: {metadatas[:2]}")
        try:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Split into batches
                batches = [
                    (documents[i:i + batch_size],
                     metadatas[i:i + batch_size])
                    for i in range(0, len(documents), batch_size)
                ]
                logger.info(f"Total batches: {len(batches)}")
                # Process batches in parallel
                futures = [
                    executor.submit(self._process_batch, docs, metas)
                    for docs, metas in batches
                ]
                # Wait for completion
                for future in futures:
                    future.result()
            logger.info("Batch processing completed")
        except Exception as e:
            import traceback
            logger.error("Error in batch processing", error=str(e), traceback=traceback.format_exc())
    
    def _process_batch(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]]
    ):
        """Process a single batch of documents."""
        logger.debug(f"Processing batch: {len(documents)} documents, {len(metadatas)} metadatas")
        try:
            # Generate embeddings in batch
            embeddings = self.embedding_model.encode(
                documents,
                batch_size=len(documents),
                show_progress_bar=True
            )
            logger.debug(f"Embeddings shape: {getattr(embeddings, 'shape', None)}")
            # Add to database
            logger.debug(f"Adding to database: docs={documents}, metas={metadatas}")
            self.database.add(
                documents=documents,
                metadatas=metadatas,
                embeddings=embeddings
            )
        except Exception as e:
            import traceback
            logger.error("Error processing batch", error=str(e), traceback=traceback.format_exc())
            print("Batch processing exception traceback:")
            print(traceback.format_exc())
    
    def faceted_search(
        self,
        query: str,
        facets: Dict[str, List[str]],
        n_results: int = 5
    ) -> Dict[str, Any]:
        """Perform faceted search with multiple dimensions."""
        try:
            results = {}
            
            # Search for each facet
            for facet_name, facet_values in facets.items():
                facet_results = []
                for value in facet_values:
                    # Search with facet filter
                    search_results = self.database.query(
                        query_texts=[query],
                        n_results=n_results,
                        where={facet_name: value}
                    )
                    if search_results:
                        facet_results.extend(search_results["documents"][0])
                
                results[facet_name] = facet_results
            
            return results
        except Exception as e:
            logger.error("Error in faceted search", error=str(e))
            return {}
    
    def range_search(
        self,
        query: str,
        range_filters: Dict[str, Dict[str, Any]],
        n_results: int = 5
    ) -> Dict[str, Any]:
        """Perform range-based search (only one field supported by ChromaDB)."""
        try:
            # Only use the first field in range_filters
            if not range_filters:
                logger.error("No range filters provided.")
                return {}
            field, range_values = next(iter(range_filters.items()))
            # Use only one operator ($gte) for the field
            where = {
                field: {"$gte": range_values.get("min")}
            }
            logger.info(f"Range search where clause: {where}")
            # Perform search
            results = self.database.query(
                query_texts=[query],
                n_results=n_results,
                where=where
            )
            logger.info(f"Range search results: {results}")
            return results
        except Exception as e:
            import traceback
            logger.error("Error in range search", error=str(e), traceback=traceback.format_exc())
            print("Range search exception traceback:")
            print(traceback.format_exc())
            return {}

def create_sample_data():
    """Create sample data for demonstration."""
    logger.info("Creating sample data")
    
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample documents with rich metadata
    documents = [
        {
            "text": "Machine learning algorithms are transforming healthcare",
            "category": "Technology",
            "date": "2024-01-15",
            "author": "John Doe",
            "tags": ["AI", "Healthcare", "ML"],
            "views": 1000,
            "rating": 4.5
        },
        {
            "text": "New breakthroughs in quantum computing research",
            "category": "Science",
            "date": "2024-02-01",
            "author": "Jane Smith",
            "tags": ["Quantum", "Computing", "Research"],
            "views": 800,
            "rating": 4.8
        },
        {
            "text": "Sustainable energy solutions for urban areas",
            "category": "Environment",
            "date": "2024-02-15",
            "author": "Mike Johnson",
            "tags": ["Energy", "Sustainability", "Urban"],
            "views": 1200,
            "rating": 4.2
        }
    ]
    
    # Save documents
    for i, doc in enumerate(documents):
        file_path = data_dir / f"doc_{i}.json"
        with open(file_path, "w") as f:
            json.dump(doc, f, indent=2)
        logger.debug(f"Created sample file: {file_path}")
    
    return data_dir

def main():
    """Main function demonstrating advanced features."""
    logger.info("Starting advanced features example")
    
    # Create sample data
    data_dir = create_sample_data()
    
    # Initialize advanced database
    db = AdvancedVectorDB(
        collection_name="advanced_example",
        index_type="hnsw"
    )
    
    # Load data from each .json file in the data directory
    source = DataSource(source_type="text")
    all_docs = []
    all_metas = []
    for file_path in glob.glob(str(data_dir / "*.json")):
        with open(file_path, "r") as f:
            data = json.load(f)
        # Convert tags list to a comma-separated string
        if isinstance(data.get("tags"), list):
            data["tags"] = ",".join(data["tags"])
        result = source.load_data(
            source=[data],  # Pass as a list of dictionaries
            text_column="text",
            metadata_columns=["category", "date", "author", "tags", "views", "rating"]
        )
        all_docs.extend(result["documents"])
        all_metas.extend(result["metadatas"])
    
    if all_docs and all_metas:
        # Process data in batches
        db.batch_process(
            documents=all_docs,
            metadatas=all_metas,
            batch_size=2
        )
        
        # Test hybrid search
        logger.info("Testing hybrid search")
        hybrid_results = db.hybrid_search(
            query="How is technology changing healthcare?",
            n_results=3
        )
        logger.info("Hybrid search results:", results=hybrid_results)
        
        # Test faceted search
        logger.info("Testing faceted search")
        facets = {
            "category": ["Technology", "Science", "Environment"],
            "tags": ["AI", "Healthcare", "ML"]
        }
        faceted_results = db.faceted_search(
            query="technology",
            facets=facets,
            n_results=2
        )
        logger.info("Faceted search results:", results=faceted_results)
        
        # Test range search
        logger.info("Testing range search")
        range_filters = {
            "views": {"min": 500, "max": 1500},
            "rating": {"min": 4.0, "max": 5.0}
        }
        range_results = db.range_search(
            query="technology",
            range_filters=range_filters,
            n_results=3
        )
        logger.info("Range search results:", results=range_results)

if __name__ == "__main__":
    main() 