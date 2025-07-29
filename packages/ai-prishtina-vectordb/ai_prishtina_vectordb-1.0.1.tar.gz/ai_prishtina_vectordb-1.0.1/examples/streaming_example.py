"""
Example script demonstrating the streaming functionality of AIPrishtina VectorDB.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
from ai_prishtina_vectordb.data_sources import DataSource

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_batch(batch: Dict[str, Any]) -> None:
    """
    Process a batch of documents.
    
    Args:
        batch: Dictionary containing documents, metadatas, and ids
    """
    logger.info(f"Processing batch with {len(batch['documents'])} documents")
    # Add your processing logic here
    for doc, meta, doc_id in zip(batch['documents'], batch['metadatas'], batch['ids']):
        logger.debug(f"Processing document {doc_id}: {doc[:100]}...")

def stream_from_file(file_path: str, batch_size: int = 1000) -> None:
    """
    Stream data from a file.
    
    Args:
        file_path: Path to the file
        batch_size: Number of items to process in each batch
    """
    logger.info(f"Streaming from file: {file_path}")
    source = DataSource()
    
    try:
        for batch in source.stream_data(
            source=file_path,
            text_column="content",
            metadata_columns=["source", "date"],
            batch_size=batch_size
        ):
            process_batch(batch)
    except Exception as e:
        logger.error(f"Error streaming from file: {str(e)}")

def stream_from_dataframe(batch_size: int = 1000) -> None:
    """
    Stream data from a pandas DataFrame.
    
    Args:
        batch_size: Number of items to process in each batch
    """
    logger.info("Creating sample DataFrame")
    df = pd.DataFrame({
        "content": [f"Document {i}" for i in range(10000)],
        "source": ["local"] * 10000,
        "date": ["2024-01-01"] * 10000
    })
    
    source = DataSource()
    try:
        for batch in source.stream_data(
            source=df,
            text_column="content",
            metadata_columns=["source", "date"],
            batch_size=batch_size
        ):
            process_batch(batch)
    except Exception as e:
        logger.error(f"Error streaming from DataFrame: {str(e)}")

def stream_from_cloud_storage(
    cloud_path: str,
    batch_size: int = 500,
    **kwargs
) -> None:
    """
    Stream data from cloud storage.
    
    Args:
        cloud_path: Cloud storage path (s3://, gs://, azure://, minio://)
        batch_size: Number of items to process in each batch
        **kwargs: Additional cloud storage configuration
    """
    logger.info(f"Streaming from cloud storage: {cloud_path}")
    source = DataSource(**kwargs)
    
    try:
        for batch in source.stream_data(
            source=cloud_path,
            text_column="text",
            metadata_columns=["source", "bucket"],
            batch_size=batch_size
        ):
            process_batch(batch)
    except Exception as e:
        logger.error(f"Error streaming from cloud storage: {str(e)}")

def main():
    """Main function demonstrating different streaming scenarios."""
    # Create a sample CSV file
    sample_data = pd.DataFrame({
        "content": [f"Document {i}" for i in range(1000)],
        "source": ["local"] * 1000,
        "date": ["2024-01-01"] * 1000
    })
    sample_file = "sample_data.csv"
    sample_data.to_csv(sample_file, index=False)
    
    try:
        # Stream from file
        logger.info("=== Streaming from file ===")
        stream_from_file(sample_file, batch_size=100)
        
        # Stream from DataFrame
        logger.info("\n=== Streaming from DataFrame ===")
        stream_from_dataframe(batch_size=100)
        
        # Stream from cloud storage (if credentials are available)
        if os.getenv("AWS_ACCESS_KEY_ID"):
            logger.info("\n=== Streaming from S3 ===")
            stream_from_cloud_storage(
                "s3://my-bucket/data/",
                batch_size=500,
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                region_name="us-west-2"
            )
        
        if os.getenv("MINIO_ENDPOINT"):
            logger.info("\n=== Streaming from MinIO ===")
            stream_from_cloud_storage(
                "minio://my-bucket/data/",
                batch_size=500,
                endpoint=os.getenv("MINIO_ENDPOINT"),
                access_key=os.getenv("MINIO_ACCESS_KEY"),
                secret_key=os.getenv("MINIO_SECRET_KEY"),
                secure=True
            )
            
    finally:
        # Clean up
        if os.path.exists(sample_file):
            os.remove(sample_file)

if __name__ == "__main__":
    main() 