"""
Caching example using AI Prishtina VectorDB.

This example demonstrates:
1. Vector search result caching
2. Cache invalidation strategies
3. Performance optimization
4. Cache hit/miss monitoring
"""

import os
from pathlib import Path
import json
from typing import List, Dict, Any, Optional
import time
import redis
from ai_prishtina_vectordb import DataSource, Database
from ai_prishtina_vectordb.logger import AIPrishtinaLogger

# Initialize logger
logger = AIPrishtinaLogger(
    name="caching_example",
    level="DEBUG",
    log_file="logs/caching.log",
    log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

class CacheManager:
    """Cache manager for vector search results."""
    
    def __init__(self, redis_client: redis.Redis, ttl: int = 3600):
        """Initialize cache manager."""
        self.redis = redis_client
        self.ttl = ttl
        self.cache_hits = 0
        self.cache_misses = 0
        logger.info("Initialized cache manager")
    
    def get_cached_results(self, query: str) -> Optional[Dict[str, Any]]:
        """Get cached search results."""
        try:
            cached = self.redis.get(query)
            if cached:
                self.cache_hits += 1
                logger.debug(f"Cache hit for query: {query}")
                return json.loads(cached)
            self.cache_misses += 1
            logger.debug(f"Cache miss for query: {query}")
            return None
        except redis.RedisError as e:
            logger.error(f"Redis error: {str(e)}")
            return None
    
    def cache_results(self, query: str, results: Dict[str, Any]) -> bool:
        """Cache search results."""
        try:
            self.redis.setex(
                query,
                self.ttl,
                json.dumps(results)
            )
            logger.debug(f"Cached results for query: {query}")
            return True
        except redis.RedisError as e:
            logger.error(f"Redis error: {str(e)}")
            return False
    
    def invalidate_cache(self, pattern: str = "*") -> bool:
        """Invalidate cache entries matching pattern."""
        try:
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cache entries")
            return True
        except redis.RedisError as e:
            logger.error(f"Redis error: {str(e)}")
            return False
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            "hits": self.cache_hits,
            "misses": self.cache_misses,
            "hit_rate": self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0
        }

class CachedSearch:
    """Cached vector search implementation."""
    
    def __init__(self, database: Database, cache_manager: CacheManager):
        """Initialize cached search."""
        self.database = database
        self.cache = cache_manager
        logger.info("Initialized cached search")
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """Perform cached vector search."""
        logger.info(f"Processing search query: {query}")
        
        # Check cache
        if use_cache:
            cached_results = self.cache.get_cached_results(query)
            if cached_results:
                logger.info("Returning cached results")
                return cached_results
        
        # Perform search
        try:
            results = self.database.query(
                query_texts=[query],
                n_results=n_results
            )
            
            # Cache results
            if use_cache:
                self.cache.cache_results(query, results)
            
            return results
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            return {"documents": [], "metadatas": [], "distances": []}

def create_sample_data():
    """Create sample data for demonstration."""
    logger.info("Creating sample data")
    
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample documents
    documents = [
        {
            "text": "Machine learning algorithms are transforming healthcare",
            "category": "Technology",
            "date": "2024-01-15"
        },
        {
            "text": "New breakthroughs in quantum computing research",
            "category": "Science",
            "date": "2024-02-01"
        },
        {
            "text": "Sustainable energy solutions for urban areas",
            "category": "Environment",
            "date": "2024-02-15"
        },
        {
            "text": "AI-powered automation in manufacturing",
            "category": "Technology",
            "date": "2024-03-01"
        },
        {
            "text": "Climate change impact on coastal regions",
            "category": "Environment",
            "date": "2024-03-15"
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
    """Main function demonstrating caching."""
    logger.info("Starting caching example")
    
    try:
        # Initialize Redis client
        redis_client = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True
        )
        
        # Create sample data
        data_dir = create_sample_data()
        
        # Load documents
        documents = load_documents(data_dir)
        
        if documents:
            # Initialize database
            database = Database(collection_name="caching_example")
            
            # Add documents to database
            database.add(
                documents=[doc["text"] for doc in documents],
                metadatas=[{
                    "category": doc["category"],
                    "date": doc["date"]
                } for doc in documents],
                ids=[f"doc_{i}" for i in range(len(documents))]
            )
            logger.info("Successfully added documents to database")
            
            # Initialize cache manager
            cache_manager = CacheManager(redis_client)
            
            # Initialize cached search
            cached_search = CachedSearch(database, cache_manager)
            
            # Test queries
            test_queries = [
                "How is technology changing healthcare?",
                "Latest developments in quantum computing",
                "Environmental impact of climate change",
                "How is technology changing healthcare?",  # Repeated query
                "Latest developments in quantum computing"  # Repeated query
            ]
            
            for query in test_queries:
                logger.info(f"\n{'='*50}")
                logger.info(f"Testing query: {query}")
                logger.info(f"{'='*50}")
                
                # First search (cache miss)
                start_time = time.time()
                results = cached_search.search(query)
                search_time = time.time() - start_time
                
                logger.info(f"Search time: {search_time:.4f} seconds")
                logger.info(f"Results: {len(results['documents'][0])} documents found")
                
                # Show cache stats
                stats = cache_manager.get_cache_stats()
                logger.info("\nCache statistics:")
                logger.info(f"- Hits: {stats['hits']}")
                logger.info(f"- Misses: {stats['misses']}")
                logger.info(f"- Hit rate: {stats['hit_rate']:.2%}")
            
            # Test cache invalidation
            logger.info("\nTesting cache invalidation")
            cache_manager.invalidate_cache()
            
            # Show final cache stats
            stats = cache_manager.get_cache_stats()
            logger.info("\nFinal cache statistics:")
            logger.info(f"- Hits: {stats['hits']}")
            logger.info(f"- Misses: {stats['misses']}")
            logger.info(f"- Hit rate: {stats['hit_rate']:.2%}")
    
    except redis.ConnectionError as e:
        logger.error(f"Redis connection error: {str(e)}")
        logger.error("Please ensure Redis server is running")
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")

if __name__ == "__main__":
    main() 