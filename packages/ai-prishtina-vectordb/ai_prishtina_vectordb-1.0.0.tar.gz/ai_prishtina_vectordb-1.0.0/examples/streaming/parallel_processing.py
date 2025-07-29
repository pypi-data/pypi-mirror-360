"""
Example demonstrating parallel processing with streaming.
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
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

def process_document(doc: str, meta: Dict[str, Any], doc_id: str) -> Dict[str, Any]:
    """
    Process a single document.
    
    Args:
        doc: Document text
        meta: Document metadata
        doc_id: Document ID
        
    Returns:
        Processed document data
    """
    # Simulate processing time
    time.sleep(0.01)
    
    # Add your processing logic here
    return {
        'id': doc_id,
        'processed_text': doc.upper(),  # Example processing
        'metadata': meta
    }

def process_batch_parallel(batch: Dict[str, Any], max_workers: int = 4) -> List[Dict[str, Any]]:
    """
    Process a batch of documents in parallel.
    
    Args:
        batch: Dictionary containing documents, metadatas, and ids
        max_workers: Maximum number of worker threads
        
    Returns:
        List of processed documents
    """
    processed_docs = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all documents for processing
        future_to_doc = {
            executor.submit(process_document, doc, meta, doc_id): doc_id
            for doc, meta, doc_id in zip(batch['documents'], batch['metadatas'], batch['ids'])
        }
        
        # Process completed futures
        for future in as_completed(future_to_doc):
            doc_id = future_to_doc[future]
            try:
                result = future.result()
                processed_docs.append(result)
            except Exception as e:
                logger.error(f"Error processing document {doc_id}: {str(e)}")
                
    return processed_docs

def stream_and_process_parallel(
    file_path: str,
    batch_size: int = 1000,
    max_workers: int = 4
) -> None:
    """
    Stream and process data in parallel.
    
    Args:
        file_path: Path to the data file
        batch_size: Number of items to process in each batch
        max_workers: Maximum number of worker threads
    """
    source = DataSource()
    total_processed = 0
    start_time = time.time()
    
    # Create progress bar
    total_docs = sum(1 for _ in open(file_path)) - 1  # Subtract header
    progress_bar = tqdm(total=total_docs, desc="Processing documents")
    
    try:
        # Stream and process data
        for batch in source.stream_data(
            source=file_path,
            text_column="content",
            metadata_columns=["source", "date"],
            batch_size=batch_size
        ):
            # Process batch in parallel
            processed_docs = process_batch_parallel(batch, max_workers)
            total_processed += len(processed_docs)
            progress_bar.update(len(batch['documents']))
            
    except Exception as e:
        logger.error(f"Error in parallel processing: {str(e)}")
    finally:
        progress_bar.close()
        
        # Print statistics
        elapsed_time = time.time() - start_time
        logger.info("\nProcessing Statistics:")
        logger.info(f"Total documents processed: {total_processed}")
        logger.info(f"Processing time: {elapsed_time:.2f} seconds")
        logger.info(f"Processing speed: {total_processed/elapsed_time:.2f} docs/sec")
        logger.info(f"Worker threads: {max_workers}")

def main():
    """Main function demonstrating parallel processing."""
    # Create a sample dataset
    logger.info("Creating sample dataset...")
    sample_data = pd.DataFrame({
        "content": [f"Document {i}" for i in range(10000)],
        "source": ["local"] * 10000,
        "date": ["2024-01-01"] * 10000
    })
    sample_file = "parallel_sample_data.csv"
    sample_data.to_csv(sample_file, index=False)
    
    try:
        # Process with different worker configurations
        for workers in [1, 2, 4, 8]:
            logger.info(f"\nProcessing with {workers} workers:")
            stream_and_process_parallel(sample_file, batch_size=500, max_workers=workers)
            
    finally:
        # Clean up
        import os
        if os.path.exists(sample_file):
            os.remove(sample_file)

if __name__ == "__main__":
    main() 