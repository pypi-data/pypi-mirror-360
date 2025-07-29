"""
Recommendation system example using AIPrishtina VectorDB.

This example demonstrates:
1. Building a content-based recommendation system
2. User preference modeling
3. Similarity-based recommendations
4. Hybrid recommendation approaches
"""

import os
from pathlib import Path
import json
import numpy as np
from typing import List, Dict, Any
from ai_prishtina_vectordb import DataSource, Database
from ai_prishtina_vectordb.logger import AIPrishtinaLogger

# Initialize logger
logger = AIPrishtinaLogger(
    name="recommendation_system_example",
    level="DEBUG",
    log_file="logs/recommendation_system.log",
    log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

class UserProfile:
    """User profile for recommendation system."""
    
    def __init__(self, user_id: str):
        """Initialize user profile."""
        self.user_id = user_id
        self.preferences = {}
        self.history = []
        logger.info(f"Initialized profile for user {user_id}")
    
    def add_preference(self, category: str, weight: float = 1.0):
        """Add user preference."""
        self.preferences[category] = weight
        logger.debug(f"Added preference for {category} with weight {weight}")
    
    def add_to_history(self, item_id: str, rating: float):
        """Add item to user history."""
        self.history.append({
            "item_id": item_id,
            "rating": rating
        })
        logger.debug(f"Added item {item_id} to history with rating {rating}")

class RecommendationSystem:
    """Content-based recommendation system."""
    
    def __init__(self, database: Database):
        """Initialize recommendation system."""
        self.database = database
        self.user_profiles = {}
        logger.info("Initialized recommendation system")
    
    def create_user_profile(self, user_id: str) -> UserProfile:
        """Create a new user profile."""
        profile = UserProfile(user_id)
        self.user_profiles[user_id] = profile
        return profile
    
    def get_user_profile(self, user_id: str) -> UserProfile:
        """Get user profile."""
        return self.user_profiles.get(user_id)
    
    def get_recommendations(
        self,
        user_id: str,
        n_recommendations: int = 5,
        min_score: float = 0.5
    ) -> List[Dict[str, Any]]:
        """Get personalized recommendations."""
        logger.info(f"Getting recommendations for user {user_id}")
        
        try:
            profile = self.get_user_profile(user_id)
            if not profile:
                logger.error(f"Profile not found for user {user_id}")
                return []
            
            # Get user preferences
            preferences = profile.preferences
            
            # Create preference query
            preference_text = " ".join([
                f"{category} " * int(weight)
                for category, weight in preferences.items()
            ])
            
            # Get recommendations
            results = self.database.query(
                query_texts=[preference_text],
                n_results=n_recommendations
            )
            
            if not results or not results["documents"] or not results["documents"][0]:
                logger.warning(f"No results found for user {user_id}")
                return []
            
            # Filter and format recommendations
            recommendations = []
            for i, (doc, metadata, score) in enumerate(zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )):
                if score >= min_score:
                    recommendations.append({
                        "item_id": results["ids"][0][i],
                        "content": doc,
                        "metadata": metadata,
                        "score": score
                    })
            
            logger.info(f"Found {len(recommendations)} recommendations for user {user_id}")
            return recommendations
        except Exception as e:
            logger.error("Error getting recommendations", error=str(e))
            return []
    
    def get_similar_items(
        self,
        item_id: str,
        n_recommendations: int = 5
    ) -> List[Dict[str, Any]]:
        """Get similar items based on content."""
        logger.info(f"Getting similar items for {item_id}")
        
        try:
            # Get item content
            item = self.database.get(item_id)
            logger.debug(f"database.get({item_id}) returned: {item}")
            if not item:
                logger.error(f"Item {item_id} not found (None returned)")
                return []
            
            # Extract document from the response
            if not isinstance(item, dict) or "documents" not in item or not item["documents"]:
                logger.error(f"Item {item_id} missing 'documents' key or empty documents: {item}")
                return []
                
            document = item["documents"][0]
            
            # Get similar items
            results = self.database.query(
                query_texts=[document],
                n_results=n_recommendations
            )
            
            if not results:
                return []
            
            # Format similar items
            similar_items = []
            for i, (doc, metadata, score) in enumerate(zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )):
                if results["ids"][0][i] != item_id:  # Exclude the original item
                    similar_items.append({
                        "item_id": results["ids"][0][i],
                        "content": doc,
                        "metadata": metadata,
                        "similarity": score
                    })
            
            return similar_items
        except Exception as e:
            logger.error(f"Error getting similar items for {item_id}: {str(e)}")
            return []

def create_sample_data():
    """Create sample data for demonstration."""
    logger.info("Creating sample data")
    
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample items
    items = [
        {
            "id": "item_1",
            "content": "Machine learning for beginners",
            "category": "Technology",
            "tags": ["AI", "Education", "Programming"]
        },
        {
            "id": "item_2",
            "content": "Advanced data science techniques",
            "category": "Technology",
            "tags": ["Data Science", "Analytics", "Programming"]
        },
        {
            "id": "item_3",
            "content": "Introduction to quantum computing",
            "category": "Science",
            "tags": ["Physics", "Computing", "Research"]
        },
        {
            "id": "item_4",
            "content": "Sustainable energy solutions",
            "category": "Environment",
            "tags": ["Green Energy", "Sustainability", "Technology"]
        },
        {
            "id": "item_5",
            "content": "Climate change and its impact",
            "category": "Environment",
            "tags": ["Climate", "Science", "Research"]
        }
    ]
    
    # Save items
    for item in items:
        file_path = data_dir / f"{item['id']}.json"
        with open(file_path, "w") as f:
            json.dump(item, f, indent=2)
        logger.debug(f"Created sample file: {file_path}")
    
    return data_dir

def load_items(data_dir: Path) -> List[Dict[str, Any]]:
    """Load items with metadata."""
    logger.info("Loading items")
    
    items = []
    for file_path in data_dir.glob("*.json"):
        try:
            with open(file_path) as f:
                item = json.load(f)
                items.append(item)
            logger.debug(f"Loaded item: {file_path}")
        except Exception as e:
            logger.error(f"Error loading item {file_path}", error=str(e))
    
    return items

def main():
    """Main function demonstrating recommendation system."""
    logger.info("Starting recommendation system example")
    
    # Create sample data
    data_dir = create_sample_data()
    
    # Load items
    items = load_items(data_dir)
    
    if items:
        # Initialize database
        database = Database(collection_name="semantic_search_example")
        
        # Add items to database
        try:
            database.add(
                documents=[item["content"] for item in items],
                metadatas=[{
                    "category": item["category"],
                    "tags": ", ".join(item["tags"])
                } for item in items],
                ids=[item["id"] for item in items]
            )
            logger.info("Successfully added items to database")
            
            # Initialize recommendation system
            recommender = RecommendationSystem(database)
            
            # Create user profiles
            users = {
                "user1": {
                    "preferences": {
                        "Technology": 2.0,
                        "Programming": 1.5
                    },
                    "history": [
                        ("item_1", 4.5),
                        ("item_2", 4.0)
                    ]
                },
                "user2": {
                    "preferences": {
                        "Science": 2.0,
                        "Research": 1.5
                    },
                    "history": [
                        ("item_3", 4.0),
                        ("item_5", 4.5)
                    ]
                }
            }
            
            # Set up user profiles
            for user_id, data in users.items():
                profile = recommender.create_user_profile(user_id)
                
                # Add preferences
                for category, weight in data["preferences"].items():
                    profile.add_preference(category, weight)
                
                # Add history
                for item_id, rating in data["history"]:
                    profile.add_to_history(item_id, rating)
            
            # Test recommendations
            for user_id in users:
                logger.info(f"Getting recommendations for {user_id}")
                recommendations = recommender.get_recommendations(user_id)
                logger.info(f"Recommendations for {user_id}:", results=recommendations)
            
            # Test similar items
            for item_id in ["item_1", "item_3", "item_4"]:
                logger.info(f"Getting similar items for {item_id}")
                similar_items = recommender.get_similar_items(item_id)
                logger.info(f"Similar items for {item_id}:", results=similar_items)
        
        except Exception as e:
            logger.error("Error in main function", error=str(e))

if __name__ == "__main__":
    main() 