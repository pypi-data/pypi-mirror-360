"""
Example demonstrating cloud storage streaming with different providers.
"""

import os
import logging
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

def stream_from_s3(
    bucket: str,
    prefix: str,
    batch_size: int = 500,
    **kwargs
) -> None:
    """
    Stream data from AWS S3.
    
    Args:
        bucket: S3 bucket name
        prefix: Object prefix
        batch_size: Number of items to process in each batch
        **kwargs: Additional S3 configuration
    """
    source = DataSource(**kwargs)
    cloud_path = f"s3://{bucket}/{prefix}"
    
    logger.info(f"Streaming from S3: {cloud_path}")
    total_processed = 0
    
    try:
        for batch in source.stream_data(
            source=cloud_path,
            text_column="text",
            metadata_columns=["source", "bucket"],
            batch_size=batch_size
        ):
            # Process batch
            total_processed += len(batch['documents'])
            logger.info(f"Processed {total_processed} documents")
            
    except Exception as e:
        logger.error(f"Error streaming from S3: {str(e)}")

def stream_from_minio(
    bucket: str,
    prefix: str,
    batch_size: int = 500,
    **kwargs
) -> None:
    """
    Stream data from MinIO.
    
    Args:
        bucket: MinIO bucket name
        prefix: Object prefix
        batch_size: Number of items to process in each batch
        **kwargs: Additional MinIO configuration
    """
    source = DataSource(**kwargs)
    cloud_path = f"minio://{bucket}/{prefix}"
    
    logger.info(f"Streaming from MinIO: {cloud_path}")
    total_processed = 0
    
    try:
        for batch in source.stream_data(
            source=cloud_path,
            text_column="text",
            metadata_columns=["source", "bucket"],
            batch_size=batch_size
        ):
            # Process batch
            total_processed += len(batch['documents'])
            logger.info(f"Processed {total_processed} documents")
            
    except Exception as e:
        logger.error(f"Error streaming from MinIO: {str(e)}")

def stream_from_gcs(
    bucket: str,
    prefix: str,
    batch_size: int = 500,
    **kwargs
) -> None:
    """
    Stream data from Google Cloud Storage.
    
    Args:
        bucket: GCS bucket name
        prefix: Object prefix
        batch_size: Number of items to process in each batch
        **kwargs: Additional GCS configuration
    """
    source = DataSource(**kwargs)
    cloud_path = f"gs://{bucket}/{prefix}"
    
    logger.info(f"Streaming from GCS: {cloud_path}")
    total_processed = 0
    
    try:
        for batch in source.stream_data(
            source=cloud_path,
            text_column="text",
            metadata_columns=["source", "bucket"],
            batch_size=batch_size
        ):
            # Process batch
            total_processed += len(batch['documents'])
            logger.info(f"Processed {total_processed} documents")
            
    except Exception as e:
        logger.error(f"Error streaming from GCS: {str(e)}")

def stream_from_azure(
    container: str,
    prefix: str,
    batch_size: int = 500,
    **kwargs
) -> None:
    """
    Stream data from Azure Blob Storage.
    
    Args:
        container: Azure container name
        prefix: Blob prefix
        batch_size: Number of items to process in each batch
        **kwargs: Additional Azure configuration
    """
    source = DataSource(**kwargs)
    cloud_path = f"azure://{container}/{prefix}"
    
    logger.info(f"Streaming from Azure: {cloud_path}")
    total_processed = 0
    
    try:
        for batch in source.stream_data(
            source=cloud_path,
            text_column="text",
            metadata_columns=["source", "container"],
            batch_size=batch_size
        ):
            # Process batch
            total_processed += len(batch['documents'])
            logger.info(f"Processed {total_processed} documents")
            
    except Exception as e:
        logger.error(f"Error streaming from Azure: {str(e)}")

def main():
    """Main function demonstrating cloud storage streaming."""
    # Example S3 streaming
    if os.getenv("AWS_ACCESS_KEY_ID"):
        stream_from_s3(
            bucket="my-bucket",
            prefix="data/",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name="us-west-2"
        )
    
    # Example MinIO streaming
    if os.getenv("MINIO_ENDPOINT"):
        stream_from_minio(
            bucket="my-bucket",
            prefix="data/",
            endpoint=os.getenv("MINIO_ENDPOINT"),
            access_key=os.getenv("MINIO_ACCESS_KEY"),
            secret_key=os.getenv("MINIO_SECRET_KEY"),
            secure=True
        )
    
    # Example GCS streaming
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        stream_from_gcs(
            bucket="my-bucket",
            prefix="data/",
            project_id=os.getenv("GOOGLE_CLOUD_PROJECT")
        )
    
    # Example Azure streaming
    if os.getenv("AZURE_STORAGE_CONNECTION_STRING"):
        stream_from_azure(
            container="my-container",
            prefix="data/",
            connection_string=os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        )

if __name__ == "__main__":
    main() 