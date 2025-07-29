"""
Content moderation example using AIPrishtina VectorDB.

This example demonstrates:
1. Content moderation using vector similarity
2. Toxic content detection
3. Content filtering and flagging
4. Moderation rules and thresholds
"""

import os
from pathlib import Path
import json
from typing import List, Dict, Any, Tuple
from ai_prishtina_vectordb import DataSource, Database
from ai_prishtina_vectordb.logger import AIPrishtinaLogger

# Initialize logger
logger = AIPrishtinaLogger(
    name="content_moderation_example",
    level="DEBUG",
    log_file="logs/content_moderation.log",
    log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

class ContentModerator:
    """Content moderation system using vector similarity."""
    
    def __init__(self, database: Database):
        """Initialize content moderator."""
        self.database = database
        self.toxic_patterns = {}
        self.moderation_rules = {}
        logger.info("Initialized content moderator")
    
    def add_toxic_pattern(self, pattern: str, category: str, severity: float):
        """Add toxic content pattern."""
        self.toxic_patterns[pattern] = {
            "category": category,
            "severity": severity
        }
        logger.debug(f"Added toxic pattern: {pattern} ({category})")
    
    def add_moderation_rule(self, category: str, threshold: float, action: str):
        """Add moderation rule."""
        self.moderation_rules[category] = {
            "threshold": threshold,
            "action": action
        }
        logger.debug(f"Added moderation rule for {category}")
    
    def check_content(
        self,
        content: str,
        min_similarity: float = 0.7
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check content for toxic patterns."""
        logger.info("Checking content for moderation")
        
        try:
            # Check against toxic patterns
            results = self.database.query(
                query_texts=[content],
                n_results=5
            )
            
            if not results:
                return False, {}
            
            # Analyze results
            matches = []
            for i, (doc, metadata, score) in enumerate(zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )):
                if score >= min_similarity:
                    pattern = doc
                    if pattern in self.toxic_patterns:
                        pattern_info = self.toxic_patterns[pattern]
                        matches.append({
                            "pattern": pattern,
                            "category": pattern_info["category"],
                            "severity": pattern_info["severity"],
                            "similarity": score
                        })
            
            if not matches:
                return False, {}
            
            # Determine moderation action
            max_severity = max(match["severity"] for match in matches)
            categories = {match["category"] for match in matches}
            
            # Check rules
            actions = []
            for category in categories:
                if category in self.moderation_rules:
                    rule = self.moderation_rules[category]
                    if max_severity >= rule["threshold"]:
                        actions.append(rule["action"])
            
            return True, {
                "matches": matches,
                "max_severity": max_severity,
                "categories": list(categories),
                "actions": actions
            }
        except Exception as e:
            logger.error("Error checking content", error=str(e))
            return False, {}
    
    def filter_content(
        self,
        content: str,
        replacement: str = "[REDACTED]"
    ) -> str:
        """Filter toxic content from text."""
        logger.info("Filtering content")
        
        try:
            # Check content
            is_toxic, matches = self.check_content(content)
            
            if not is_toxic:
                return content
            
            # Filter toxic patterns
            filtered_content = content
            for match in matches["matches"]:
                pattern = match["pattern"]
                filtered_content = filtered_content.replace(pattern, replacement)
            
            return filtered_content
        except Exception as e:
            logger.error("Error filtering content", error=str(e))
            return content

def create_sample_data():
    """Create sample data for demonstration."""
    logger.info("Creating sample data")
    
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample toxic patterns
    patterns = [
        {
            "pattern": "hate speech example",
            "category": "Hate Speech",
            "severity": 0.9
        },
        {
            "pattern": "harassment example",
            "category": "Harassment",
            "severity": 0.8
        },
        {
            "pattern": "inappropriate content",
            "category": "Inappropriate",
            "severity": 0.7
        },
        {
            "pattern": "spam content",
            "category": "Spam",
            "severity": 0.6
        }
    ]
    
    # Save patterns
    for pattern in patterns:
        file_path = data_dir / f"pattern_{pattern['category'].lower()}.json"
        with open(file_path, "w") as f:
            json.dump(pattern, f, indent=2)
        logger.debug(f"Created pattern file: {file_path}")
    
    return data_dir

def load_patterns(data_dir: Path) -> List[Dict[str, Any]]:
    """Load toxic patterns."""
    logger.info("Loading toxic patterns")
    
    patterns = []
    for file_path in data_dir.glob("*.json"):
        try:
            with open(file_path) as f:
                pattern = json.load(f)
                patterns.append(pattern)
            logger.debug(f"Loaded pattern: {file_path}")
        except Exception as e:
            logger.error(f"Error loading pattern {file_path}", error=str(e))
    
    return patterns

def main():
    """Main function demonstrating content moderation."""
    logger.info("Starting content moderation example")
    
    # Create sample data
    data_dir = create_sample_data()
    
    # Load patterns
    patterns = load_patterns(data_dir)
    
    if patterns:
        # Initialize database
        database = Database(collection_name="content_moderation_example")
        
        # Add patterns to database
        try:
            database.add(
                documents=[pattern["pattern"] for pattern in patterns],
                metadatas=[{
                    "category": pattern["category"],
                    "severity": pattern["severity"]
                } for pattern in patterns],
                ids=[f"pattern_{i}" for i in range(len(patterns))]
            )
            logger.info("Successfully added patterns to database")
            
            # Initialize content moderator
            moderator = ContentModerator(database)
            
            # Add patterns to moderator
            for pattern in patterns:
                moderator.add_toxic_pattern(
                    pattern=pattern["pattern"],
                    category=pattern["category"],
                    severity=pattern["severity"]
                )
            
            # Add moderation rules
            rules = {
                "Hate Speech": {"threshold": 0.8, "action": "block"},
                "Harassment": {"threshold": 0.7, "action": "flag"},
                "Inappropriate": {"threshold": 0.6, "action": "review"},
                "Spam": {"threshold": 0.5, "action": "filter"}
            }
            
            for category, rule in rules.items():
                moderator.add_moderation_rule(
                    category=category,
                    threshold=rule["threshold"],
                    action=rule["action"]
                )
            
            # Test different content
            test_cases = [
                {
                    "name": "Hate speech detection",
                    "content": "This message contains hate speech example targeting minorities"
                },
                {
                    "name": "Harassment detection",
                    "content": "You are worthless and this is a harassment example"
                },
                {
                    "name": "Inappropriate content",
                    "content": "This post contains inappropriate content and should be reviewed"
                },
                {
                    "name": "Spam detection",
                    "content": "Buy now! Limited time offer! This is spam content!"
                },
                {
                    "name": "Clean content",
                    "content": "This is a normal message without any issues"
                }
            ]
            
            for case in test_cases:
                logger.info(f"\n{'='*50}")
                logger.info(f"Testing {case['name']}")
                logger.info(f"{'='*50}")
                
                # Check content
                is_toxic, results = moderator.check_content(case["content"])
                
                logger.info(f"Content: {case['content']}")
                logger.info(f"Is toxic: {is_toxic}")
                
                if is_toxic:
                    logger.info("Moderation details:")
                    logger.info(f"- Categories found: {', '.join(results['categories'])}")
                    logger.info(f"- Maximum severity: {results['max_severity']:.2f}")
                    logger.info(f"- Actions required: {', '.join(results['actions'])}")
                    
                    # Show matches
                    logger.info("\nPattern matches:")
                    for match in results['matches']:
                        logger.info(f"- Pattern: {match['pattern']}")
                        logger.info(f"  Category: {match['category']}")
                        logger.info(f"  Severity: {match['severity']:.2f}")
                        logger.info(f"  Similarity: {match['similarity']:.2f}")
                    
                    # Show filtered content
                    filtered = moderator.filter_content(case["content"])
                    logger.info(f"\nFiltered content: {filtered}")
                else:
                    logger.info("Content passed moderation checks")
        
        except Exception as e:
            logger.error("Error in main function", error=str(e))

if __name__ == "__main__":
    main() 