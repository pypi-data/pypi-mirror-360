"""
Example script demonstrating MinIO integration with AIPrishtina VectorDB.
"""

import os
import logging
from ai_prishtina_vectordb.data_sources import DataSource

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_minio_credentials():
    """Setup MinIO credentials from environment variables."""
    required_vars = [
        'MINIO_ENDPOINT',
        'MINIO_ACCESS_KEY',
        'MINIO_SECRET_KEY'
    ]
    
    for var in required_vars:
        if not os.getenv(var):
            logger.error(f"Missing required environment variable: {var}")
            return False
    
    return True

def load_from_minio(bucket_name: str, prefix: str = ""):
    """Load data from MinIO."""
    logger.info(f"Loading data from MinIO bucket: {bucket_name}")
    
    if not setup_minio_credentials():
        logger.error("MinIO credentials not properly configured")
        return None
    
    try:
        # Initialize MinIO data source
        source = DataSource(
            source_type="minio",
            endpoint=os.getenv('MINIO_ENDPOINT'),
            access_key=os.getenv('MINIO_ACCESS_KEY'),
            secret_key=os.getenv('MINIO_SECRET_KEY'),
            secure=True  # Use SSL/TLS
        )
        
        # Load data from MinIO
        result = source.load_data(
            source=f"minio://{bucket_name}/{prefix}",
            metadata_columns=["source", "bucket", "object"]
        )
        
        logger.info("Successfully loaded data from MinIO")
        return result
        
    except Exception as e:
        logger.error(f"Error loading data from MinIO: {str(e)}")
        return None

def main():
    """Main function demonstrating MinIO usage."""
    # Example usage
    bucket_name = "my-bucket"
    prefix = "data/"
    
    # Load data from MinIO
    data = load_from_minio(bucket_name, prefix)
    
    if data:
        logger.info(f"Loaded {len(data['documents'])} documents")
        logger.info(f"Sample metadata: {data['metadatas'][0] if data['metadatas'] else 'No metadata'}")
    else:
        logger.error("Failed to load data from MinIO")

if __name__ == "__main__":
    main() 