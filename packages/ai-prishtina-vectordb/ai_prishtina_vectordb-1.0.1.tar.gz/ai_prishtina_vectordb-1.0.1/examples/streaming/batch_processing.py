"""
Example demonstrating advanced batch processing with streaming.
"""

import logging
import time
from typing import Dict, Any, List
import pandas as pd
from tqdm import tqdm
from ai_prishtina_vectordb.data_sources import DataSource

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BatchProcessor:
    """Advanced batch processor with progress tracking and error handling."""
    
    def __init__(self, batch_size: int = 1000, max_retries: int = 3):
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.processed_count = 0
        self.error_count = 0
        self.start_time = None
        
    def process_batch(self, batch: Dict[str, Any]) -> None:
        """
        Process a batch with retry logic and progress tracking.
        
        Args:
            batch: Dictionary containing documents, metadatas, and ids
        """
        retries = 0
        while retries < self.max_retries:
            try:
                # Simulate processing time
                time.sleep(0.1)
                
                # Process each document in the batch
                for doc, meta, doc_id in zip(batch['documents'], batch['metadatas'], batch['ids']):
                    # Add your processing logic here
                    logger.debug(f"Processing document {doc_id}: {doc[:100]}...")
                    self.processed_count += 1
                    
                return  # Success, exit retry loop
                
            except Exception as e:
                retries += 1
                if retries == self.max_retries:
                    logger.error(f"Failed to process batch after {self.max_retries} retries: {str(e)}")
                    self.error_count += len(batch['documents'])
                else:
                    logger.warning(f"Retry {retries}/{self.max_retries} after error: {str(e)}")
                    time.sleep(1)  # Wait before retry
                    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        if not self.start_time:
            return {}
            
        elapsed_time = time.time() - self.start_time
        return {
            'processed_count': self.processed_count,
            'error_count': self.error_count,
            'elapsed_time': elapsed_time,
            'documents_per_second': self.processed_count / elapsed_time if elapsed_time > 0 else 0
        }

def process_large_dataset(file_path: str, batch_size: int = 1000) -> None:
    """
    Process a large dataset with progress tracking and error handling.
    
    Args:
        file_path: Path to the dataset file
        batch_size: Number of items to process in each batch
    """
    # Initialize processor and data source
    processor = BatchProcessor(batch_size=batch_size)
    source = DataSource()
    
    # Create progress bar
    total_docs = sum(1 for _ in open(file_path)) - 1  # Subtract header
    progress_bar = tqdm(total=total_docs, desc="Processing documents")
    
    try:
        processor.start_time = time.time()
        
        # Stream and process data
        for batch in source.stream_data(
            source=file_path,
            text_column="content",
            metadata_columns=["source", "date"],
            batch_size=batch_size
        ):
            processor.process_batch(batch)
            progress_bar.update(len(batch['documents']))
            
    except Exception as e:
        logger.error(f"Error processing dataset: {str(e)}")
    finally:
        progress_bar.close()
        
        # Print statistics
        stats = processor.get_stats()
        logger.info("\nProcessing Statistics:")
        logger.info(f"Total documents processed: {stats['processed_count']}")
        logger.info(f"Errors encountered: {stats['error_count']}")
        logger.info(f"Processing time: {stats['elapsed_time']:.2f} seconds")
        logger.info(f"Processing speed: {stats['documents_per_second']:.2f} docs/sec")

def main():
    """Main function demonstrating batch processing."""
    # Create a sample large dataset
    logger.info("Creating sample dataset...")
    sample_data = pd.DataFrame({
        "content": [f"Document {i}" for i in range(10000)],
        "source": ["local"] * 10000,
        "date": ["2024-01-01"] * 10000
    })
    sample_file = "large_sample_data.csv"
    sample_data.to_csv(sample_file, index=False)
    
    try:
        # Process the dataset
        logger.info("Starting batch processing...")
        process_large_dataset(sample_file, batch_size=500)
        
    finally:
        # Clean up
        import os
        if os.path.exists(sample_file):
            os.remove(sample_file)

if __name__ == "__main__":
    main() 