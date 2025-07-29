"""
Cloud storage integration example using AIPrishtina VectorDB.

This example demonstrates:
1. Loading data from different cloud storage providers (S3, GCS, Azure)
2. Handling different file types from cloud storage
3. Managing credentials and authentication
4. Logging operations
"""

import os
from pathlib import Path
import boto3
from google.cloud import storage
from azure.storage.blob import BlobServiceClient
from ai_prishtina_vectordb import DataSource, Database
from ai_prishtina_vectordb.logger import AIPrishtinaLogger

# Initialize logger
logger = AIPrishtinaLogger(
    name="cloud_storage_example",
    level="DEBUG",
    log_file="logs/cloud_storage.log"
)

def setup_aws_credentials():
    """Setup AWS credentials for S3 access."""
    logger.info("Setting up AWS credentials")
    try:
        # You can set these in your environment variables
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        
        if not aws_access_key or not aws_secret_key:
            logger.warning("AWS credentials not found in environment variables")
            return False
            
        return True
    except Exception as e:
        logger.error("Error setting up AWS credentials", error=str(e))
        return False

def setup_gcp_credentials():
    """Setup GCP credentials for Google Cloud Storage access."""
    logger.info("Setting up GCP credentials")
    try:
        # You can set this in your environment variables
        gcp_credentials = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        
        if not gcp_credentials:
            logger.warning("GCP credentials not found in environment variables")
            return False
            
        return True
    except Exception as e:
        logger.error("Error setting up GCP credentials", error=str(e))
        return False

def setup_azure_credentials():
    """Setup Azure credentials for Blob Storage access."""
    logger.info("Setting up Azure credentials")
    try:
        # You can set these in your environment variables
        azure_connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        
        if not azure_connection_string:
            logger.warning("Azure credentials not found in environment variables")
            return False
            
        return True
    except Exception as e:
        logger.error("Error setting up Azure credentials", error=str(e))
        return False

def load_from_s3(bucket_name: str, prefix: str = ""):
    """Load data from Amazon S3."""
    logger.info(f"Loading data from S3 bucket: {bucket_name}")
    
    if not setup_aws_credentials():
        logger.error("AWS credentials not properly configured")
        return None
    
    try:
        source = DataSource(source_type="s3")
        result = source.load_data(
            source=f"s3://{bucket_name}/{prefix}",
            metadata_columns=["source", "bucket", "key"]
        )
        logger.info("Successfully loaded data from S3")
        return result
    except Exception as e:
        logger.error("Error loading data from S3", error=str(e))
        return None

def load_from_gcs(bucket_name: str, prefix: str = ""):
    """Load data from Google Cloud Storage."""
    logger.info(f"Loading data from GCS bucket: {bucket_name}")
    
    if not setup_gcp_credentials():
        logger.error("GCP credentials not properly configured")
        return None
    
    try:
        source = DataSource(source_type="gcs")
        result = source.load_data(
            source=f"gs://{bucket_name}/{prefix}",
            metadata_columns=["source", "bucket", "blob"]
        )
        logger.info("Successfully loaded data from GCS")
        return result
    except Exception as e:
        logger.error("Error loading data from GCS", error=str(e))
        return None

def load_from_azure(container_name: str, prefix: str = ""):
    """Load data from Azure Blob Storage."""
    logger.info(f"Loading data from Azure container: {container_name}")
    
    if not setup_azure_credentials():
        logger.error("Azure credentials not properly configured")
        return None
    
    try:
        source = DataSource(source_type="azure")
        result = source.load_data(
            source=f"azure://{container_name}/{prefix}",
            metadata_columns=["source", "container", "blob"]
        )
        logger.info("Successfully loaded data from Azure")
        return result
    except Exception as e:
        logger.error("Error loading data from Azure", error=str(e))
        return None

def perform_search(database: Database, query: str, n_results: int = 3):
    """Perform similarity search."""
    logger.info(f"Performing search for query: {query}")
    
    try:
        results = database.query(
            query_texts=[query],
            n_results=n_results
        )
        logger.info(f"Found {len(results['documents'][0])} results")
        return results
    except Exception as e:
        logger.error("Error performing search", error=str(e))
        return None

def main():
    """Main function demonstrating cloud storage integration."""
    logger.info("Starting cloud storage example")
    
    # Initialize database
    database = Database()
    
    # Example S3 configuration
    s3_bucket = "your-s3-bucket"
    s3_prefix = "data/"
    
    # Example GCS configuration
    gcs_bucket = "your-gcs-bucket"
    gcs_prefix = "data/"
    
    # Example Azure configuration
    azure_container = "your-azure-container"
    azure_prefix = "data/"
    
    # Load data from different cloud providers
    cloud_results = {}
    
    # Load from S3
    s3_result = load_from_s3(s3_bucket, s3_prefix)
    if s3_result:
        cloud_results["s3"] = s3_result
    
    # Load from GCS
    gcs_result = load_from_gcs(gcs_bucket, gcs_prefix)
    if gcs_result:
        cloud_results["gcs"] = gcs_result
    
    # Load from Azure
    azure_result = load_from_azure(azure_container, azure_prefix)
    if azure_result:
        cloud_results["azure"] = azure_result
    
    # Add data to database
    for provider, result in cloud_results.items():
        logger.info(f"Adding data from {provider} to database")
        try:
            database.add(
                documents=result["documents"],
                metadatas=result["metadatas"],
                ids=result["ids"]
            )
            logger.debug(f"Successfully added data from {provider}")
        except Exception as e:
            logger.error(f"Error adding data from {provider}", error=str(e))
    
    # Perform searches
    queries = [
        "Find documents about machine learning",
        "Search for financial reports",
        "Look for technical documentation"
    ]
    
    for query in queries:
        logger.info(f"Processing query: {query}")
        results = perform_search(database, query)
        if results:
            logger.info("Search results:", results=results)

if __name__ == "__main__":
    main() 