"""
Fine-tuning example using AIPrishtina VectorDB.

This example demonstrates:
1. Fine-tuning embedding models for specific domains
2. Using custom training data
3. Evaluating model performance
4. Logging operations
"""

import os
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader
from ai_prishtina_vectordb import DataSource, Database
from ai_prishtina_vectordb.logger import AIPrishtinaLogger

# Initialize logger
logger = AIPrishtinaLogger(
    name="fine_tuning_example",
    level="DEBUG",
    log_file="logs/fine_tuning.log"
)

def create_training_data():
    """Create sample training data for fine-tuning."""
    logger.info("Creating training data")
    
    # Create data directory
    data_dir = Path("data/fine_tuning")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample training pairs (similar documents)
    training_pairs = [
        # Technology domain
        (
            "Machine learning algorithms are used for pattern recognition",
            "AI systems can identify patterns in large datasets"
        ),
        (
            "Deep learning models require significant computational resources",
            "Neural networks need powerful hardware for training"
        ),
        
        # Medical domain
        (
            "The patient showed symptoms of respiratory infection",
            "Clinical signs indicated a lung-related illness"
        ),
        (
            "The treatment protocol includes regular medication",
            "Patient care plan involves daily drug administration"
        ),
        
        # Legal domain
        (
            "The contract specifies the terms of agreement",
            "The legal document outlines the conditions"
        ),
        (
            "The court ruling established a precedent",
            "The judicial decision set a legal standard"
        )
    ]
    
    # Save training pairs
    for i, (text1, text2) in enumerate(training_pairs):
        pair_dir = data_dir / f"pair_{i}"
        pair_dir.mkdir(exist_ok=True)
        
        with open(pair_dir / "doc1.txt", "w") as f:
            f.write(text1)
        with open(pair_dir / "doc2.txt", "w") as f:
            f.write(text2)
        
        logger.debug(f"Created training pair {i}")
    
    return data_dir

def prepare_training_examples(data_dir: Path):
    """Prepare training examples for fine-tuning."""
    logger.info("Preparing training examples")
    
    training_examples = []
    
    # Read training pairs
    for pair_dir in data_dir.iterdir():
        if pair_dir.is_dir():
            with open(pair_dir / "doc1.txt") as f:
                text1 = f.read().strip()
            with open(pair_dir / "doc2.txt") as f:
                text2 = f.read().strip()
            
            # Create positive example (similar documents)
            training_examples.append(InputExample(texts=[text1, text2], label=1.0))
            
            # Create negative example (different documents)
            if len(training_examples) > 1:
                training_examples.append(InputExample(texts=[text1, training_examples[-2].texts[0]], label=0.0))
    
    return training_examples

def fine_tune_model(base_model_name: str, training_examples: list, output_path: str):
    """Fine-tune the embedding model."""
    logger.info(f"Fine-tuning model: {base_model_name}")
    
    try:
        # Load base model
        model = SentenceTransformer(base_model_name)
        
        # Create data loader
        train_dataloader = DataLoader(training_examples, shuffle=True, batch_size=16)
        
        # Define loss function
        train_loss = losses.CosineSimilarityLoss(model)
        
        # Fine-tune model
        model.fit(
            train_objectives=[(train_dataloader, train_loss)],
            epochs=3,
            warmup_steps=100,
            show_progress_bar=True
        )
        
        # Save fine-tuned model
        model.save(output_path)
        logger.info(f"Fine-tuned model saved to: {output_path}")
        
        return model
    except Exception as e:
        logger.error("Error fine-tuning model: " + str(e))
        return None

def evaluate_model(model: SentenceTransformer, test_queries: list, test_documents: list):
    """Evaluate model performance."""
    logger.info("Evaluating model performance")
    
    try:
        # Encode queries and documents
        query_embeddings = model.encode(test_queries)
        doc_embeddings = model.encode(test_documents)
        
        # Calculate similarities
        similarities = np.dot(query_embeddings, doc_embeddings.T)
        
        # Log results
        for i, query in enumerate(test_queries):
            logger.info(f"Query: {query}")
            for j, doc in enumerate(test_documents):
                logger.info(f"Document: {doc}")
                logger.info(f"Similarity: {similarities[i][j]:.4f}")
        
        return similarities
    except Exception as e:
        logger.error("Error evaluating model", error=str(e))
        return None

def main():
    """Main function demonstrating fine-tuning."""
    logger.info("Starting fine-tuning example")
    
    # Create training data
    data_dir = create_training_data()
    
    # Prepare training examples
    training_examples = prepare_training_examples(data_dir)
    
    # Fine-tune model
    base_model = "all-MiniLM-L6-v2"
    output_path = "models/fine_tuned_model"
    fine_tuned_model = fine_tune_model(base_model, training_examples, output_path)
    
    if fine_tuned_model:
        # Test queries and documents
        test_queries = [
            "How do machine learning systems work?",
            "What are the symptoms of respiratory illness?",
            "What are the terms of the legal agreement?"
        ]
        
        test_documents = [
            "AI algorithms can recognize patterns in data",
            "The patient exhibited signs of lung infection",
            "The contract outlines the agreement conditions"
        ]
        
        # Evaluate model
        similarities = evaluate_model(fine_tuned_model, test_queries, test_documents)
        
        if similarities is not None:
            logger.info("Model evaluation completed successfully")
            
            # Use fine-tuned model with VectorDB
            source = DataSource(
                source_type="text"
            )
            
            # Load and process data
            result = source.load_data(
                source=data_dir,
                metadata_columns=["source", "model"]
            )
            
            if result:
                # Initialize database
                database = Database()
                
                # Add data to database
                database.add(
                    documents=result["documents"],
                    metadatas=result["metadatas"],
                    ids=result["ids"]
                )
                
                # Perform searches
                for query in test_queries:
                    logger.info(f"Processing query: {query}")
                    search_results = database.query(
                        query_texts=[query],
                        n_results=3
                    )
                    if search_results:
                        logger.info("Search results:", results=search_results)

if __name__ == "__main__":
    main() 