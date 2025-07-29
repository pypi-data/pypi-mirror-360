"""
Semantic search engine example using AI Prishtina VectorDB.

This example demonstrates:
1. Building a semantic search engine
2. Implementing advanced search features
3. Handling different document types
4. Search result ranking and filtering
"""

import os
from pathlib import Path
import json
from typing import List, Dict, Any
from datetime import datetime
import time
from ai_prishtina_vectordb import DataSource, Database
from ai_prishtina_vectordb.logger import AIPrishtinaLogger

# Initialize logger
logger = AIPrishtinaLogger(
    name="semantic_search_example",
    level="DEBUG",
    log_file="logs/semantic_search.log",
    log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def date_to_timestamp(date_str: str) -> int:
    """Convert date string to timestamp."""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return int(dt.timestamp())

class SemanticSearchEngine:
    """Semantic search engine implementation."""
    
    def __init__(self, database: Database):
        """Initialize search engine."""
        self.database = database
        logger.info("Initialized semantic search engine")
    
    def search(
        self,
        query: str,
        filters: Dict[str, Any] = None,
        n_results: int = 5,
        min_score: float = 0.5
    ) -> Dict[str, Any]:
        """Perform semantic search with filters."""
        logger.info(f"Processing search query: {query}")
        logger.debug(f"Search filters: {filters}")
        
        try:
            # Perform search
            results = self.database.query(
                query_texts=[query],
                n_results=n_results,
                where=filters
            )
            
            if not results:
                logger.info("No results found")
                return {"results": [], "total": 0}
            
            # Filter results by score
            filtered_results = []
            for i, (doc, metadata, score) in enumerate(zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )):
                if score >= min_score:
                    filtered_results.append({
                        "document": doc,
                        "metadata": metadata,
                        "score": score
                    })
            
            # Log results in a readable format
            logger.info(f"Found {len(filtered_results)} results:")
            for idx, result in enumerate(filtered_results, 1):
                logger.info(f"\nResult {idx}:")
                logger.info(f"Document: {result['document']}")
                logger.info(f"Metadata: {result['metadata']}")
                logger.info(f"Score: {result['score']:.4f}")
            
            return {
                "results": filtered_results,
                "total": len(filtered_results)
            }
        except Exception as e:
            import traceback
            error_msg = f"Error performing search: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            print(f"Search error details:\n{error_msg}")
            return {"results": [], "total": 0}
    
    def search_by_category(
        self,
        query: str,
        category: str,
        n_results: int = 5
    ) -> Dict[str, Any]:
        """Search within a specific category."""
        return self.search(
            query=query,
            filters={"category": category},
            n_results=n_results
        )
    
    def search_by_date_range(
        self,
        query: str,
        start_date: str,
        end_date: str,
        n_results: int = 5
    ) -> Dict[str, Any]:
        """Search within a date range using timestamps."""
        # Convert dates to timestamps
        start_timestamp = date_to_timestamp(start_date)
        end_timestamp = date_to_timestamp(end_date)
        
        # Use timestamp for comparison
        return self.search(
            query=query,
            filters={
                "date": {
                    "$gte": start_timestamp
                }
            },
            n_results=n_results
        )

def create_sample_data():
    """Create sample data for demonstration."""
    logger.info("Creating sample data")
    
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample documents with metadata
    documents = [
        {
            "text": "Machine learning algorithms are transforming healthcare",
            "category": "Technology",
            "date": date_to_timestamp("2024-01-15"),
            "author": "John Doe"
        },
        {
            "text": "New breakthroughs in quantum computing research",
            "category": "Science",
            "date": date_to_timestamp("2024-02-01"),
            "author": "Jane Smith"
        },
        {
            "text": "Sustainable energy solutions for urban areas",
            "category": "Environment",
            "date": date_to_timestamp("2024-02-15"),
            "author": "Mike Johnson"
        },
        {
            "text": "AI-powered automation in manufacturing",
            "category": "Technology",
            "date": date_to_timestamp("2024-03-01"),
            "author": "Sarah Wilson"
        },
        {
            "text": "Climate change impact on coastal regions",
            "category": "Environment",
            "date": date_to_timestamp("2024-03-15"),
            "author": "David Brown"
        }
    ]
    
    # Save documents
    for i, doc in enumerate(documents):
        file_path = data_dir / f"doc_{i}.json"
        with open(file_path, "w") as f:
            json.dump(doc, f, indent=2)
        logger.debug(f"Created sample file: {file_path}")
    
    return data_dir

def load_documents(data_dir: Path) -> List[Dict[str, Any]]:
    """Load documents with metadata."""
    logger.info("Loading documents")
    
    documents = []
    for file_path in data_dir.glob("*.json"):
        try:
            with open(file_path) as f:
                doc = json.load(f)
                documents.append(doc)
            logger.debug(f"Loaded document: {file_path}")
        except Exception as e:
            logger.error(f"Error loading document {file_path}", error=str(e))
    
    return documents

def main():
    """Main function demonstrating semantic search."""
    logger.info("Starting semantic search example")
    
    # Create sample data
    data_dir = create_sample_data()
    
    # Load documents
    documents = load_documents(data_dir)
    
    if documents:
        # Initialize database
        database = Database(collection_name="semantic_search_example")
        
        # Add documents to database
        try:
            database.add(
                documents=[doc["text"] for doc in documents],
                metadatas=[{
                    "category": doc["category"],
                    "date": doc["date"],
                    "author": doc["author"]
                } for doc in documents],
                ids=[f"doc_{i}" for i in range(len(documents))]
            )
            logger.info("Successfully added documents to database")
            
            # Initialize search engine
            search_engine = SemanticSearchEngine(database)
            
            # Test different search scenarios
            test_cases = [
                {
                    "name": "Basic search",
                    "query": "How is technology changing healthcare?",
                    "filters": None
                },
                {
                    "name": "Category search",
                    "query": "Latest developments in technology",
                    "category": "Technology"
                },
                {
                    "name": "Date range search",
                    "query": "Recent environmental changes",
                    "start_date": "2024-02-01",
                    "end_date": "2024-03-15"
                }
            ]
            
            for case in test_cases:
                logger.info(f"\n{'='*50}")
                logger.info(f"Testing {case['name']}")
                logger.info(f"{'='*50}")
                
                if case["name"] == "Basic search":
                    results = search_engine.search(
                        query=case["query"],
                        filters=case["filters"]
                    )
                elif case["name"] == "Category search":
                    results = search_engine.search_by_category(
                        query=case["query"],
                        category=case["category"]
                    )
                else:  # Date range search
                    results = search_engine.search_by_date_range(
                        query=case["query"],
                        start_date=case["start_date"],
                        end_date=case["end_date"]
                    )
                
                logger.info(f"\nSearch completed for {case['name']}")
                logger.info(f"Total results: {results['total']}")
        
        except Exception as e:
            logger.error("Error in main function", error=str(e))

if __name__ == "__main__":
    main() 