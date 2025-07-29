"""
Batch processing example using AI Prishtina VectorDB.

This example demonstrates:
1. Processing large datasets in batches
2. Memory-efficient data loading
3. Progress tracking
4. Error handling
"""

import os
from pathlib import Path
import pandas as pd
import numpy as np
from typing import List, Dict, Any
from tqdm import tqdm
from ai_prishtina_vectordb import DataSource, Database
from ai_prishtina_vectordb.logger import AIPrishtinaLogger

# Initialize logger
logger = AIPrishtinaLogger(
    name="batch_processing_example",
    level="DEBUG",
    log_file="logs/batch_processing.log",
    log_format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def create_large_dataset(size: int = 10000) -> Path:
    """Create a large dataset for demonstration."""
    logger.info(f"Creating large dataset with {size} records")
    
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Create chunks of data
    chunk_size = 1000
    n_chunks = (size + chunk_size - 1) // chunk_size
    
    for i in range(n_chunks):
        # Generate random data
        n_records = min(chunk_size, size - i * chunk_size)
        data = {
            "text": [f"Sample text {j}" for j in range(n_records)],
            "category": np.random.choice(["A", "B", "C"], n_records),
            "value": np.random.rand(n_records)
        }
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Save to CSV
        chunk_path = data_dir / f"chunk_{i}.csv"
        df.to_csv(chunk_path, index=False)
        logger.debug(f"Created chunk file: {chunk_path}")
    
    return data_dir

def process_batch(
    source: DataSource,
    batch_files: List[Path],
    batch_id: int
) -> Dict[str, Any]:
    """Process a batch of files."""
    logger.info(f"Processing batch {batch_id}")
    
    try:
        # Load data from CSV files
        data = []
        for file_path in batch_files:
            df = pd.read_csv(file_path)
            data.extend(df.to_dict('records'))
        
        # Process batch
        result = source.load_data(
            source=data,
            text_column="text",
            metadata_columns=["category", "value"]
        )
        
        return {
            "batch_id": batch_id,
            "n_records": len(data),
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error processing batch {batch_id}: {str(e)}")
        return {
            "batch_id": batch_id,
            "n_records": 0,
            "status": "error",
            "error": str(e)
        }

def batch_process_dataset(
    data_dir: Path,
    batch_size: int = 1000
) -> List[Dict[str, Any]]:
    """Process dataset in batches."""
    logger.info("Starting batch processing")
    
    # Initialize data source
    source = DataSource()
    
    # Get all files
    files = list(data_dir.glob("*.csv"))
    total_files = len(files)
    logger.info(f"Found {total_files} files to process")
    
    # Process in batches
    results = []
    for batch_id, i in enumerate(range(0, total_files, batch_size)):
        batch_files = files[i:i + batch_size]
        logger.info(f"Processing batch {batch_id} ({len(batch_files)} files)")
        
        # Process batch with progress bar
        with tqdm(total=len(batch_files), desc=f"Batch {batch_id}") as pbar:
            batch_result = process_batch(source, batch_files, batch_id)
            pbar.update(len(batch_files))
        
        results.append(batch_result)
    
    return results

def main():
    """Main function demonstrating batch processing."""
    logger.info("Starting batch processing example")
    
    # Create sample data
    data_dir = create_large_dataset(size=10000)
    
    # Process dataset in batches
    batch_results = batch_process_dataset(data_dir, batch_size=1000)
    
    # Print results
    successful_batches = sum(1 for r in batch_results if r["status"] == "success")
    total_records = sum(r["n_records"] for r in batch_results)
    
    logger.info(f"Processing complete:")
    logger.info(f"- Total batches: {len(batch_results)}")
    logger.info(f"- Successful batches: {successful_batches}")
    logger.info(f"- Total records processed: {total_records}")

if __name__ == "__main__":
    main() 