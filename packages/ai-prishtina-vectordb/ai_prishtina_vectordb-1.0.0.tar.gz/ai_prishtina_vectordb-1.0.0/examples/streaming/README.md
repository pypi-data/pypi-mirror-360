# Streaming Examples

This directory contains example scripts demonstrating different streaming capabilities of the AIPrishtina VectorDB library.

## Examples

### 1. Batch Processing (`batch_processing.py`)
Demonstrates advanced batch processing with:
- Progress tracking
- Error handling and retries
- Processing statistics
- Memory-efficient processing

```python
from aiprishtina_vectordb.data_sources import DataSource

# Initialize data source
source = DataSource()

# Process large dataset with batch processing
for batch in source.stream_data(
    source="large_data.csv",
    text_column="content",
    metadata_columns=["source", "date"],
    batch_size=1000
):
    process_batch(batch)
```

### 2. Parallel Processing (`parallel_processing.py`)
Shows how to process data in parallel with:
- Thread pool execution
- Configurable worker threads
- Progress tracking
- Performance comparison

```python
# Process data in parallel
with ThreadPoolExecutor(max_workers=4) as executor:
    for batch in source.stream_data(source="data.csv"):
        process_batch_parallel(batch, max_workers=4)
```

### 3. Cloud Storage (`cloud_storage.py`)
Examples for streaming from different cloud storage providers:
- AWS S3
- MinIO
- Google Cloud Storage
- Azure Blob Storage

```python
# Stream from S3
for batch in source.stream_data(
    source="s3://my-bucket/data/",
    text_column="text",
    metadata_columns=["source", "bucket"],
    batch_size=500
):
    process_batch(batch)
```

## Requirements

Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Set up environment variables for cloud storage credentials:
```bash
# AWS S3
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"

# MinIO
export MINIO_ENDPOINT="your_endpoint"
export MINIO_ACCESS_KEY="your_access_key"
export MINIO_SECRET_KEY="your_secret_key"

# Google Cloud Storage
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
export GOOGLE_CLOUD_PROJECT="your_project_id"

# Azure Blob Storage
export AZURE_STORAGE_CONNECTION_STRING="your_connection_string"
```

2. Run the examples:
```bash
# Batch processing
python batch_processing.py

# Parallel processing
python parallel_processing.py

# Cloud storage
python cloud_storage.py
```

## Best Practices

1. **Batch Size Selection**
   - Choose batch size based on available memory
   - Monitor memory usage during processing
   - Adjust batch size for optimal performance

2. **Error Handling**
   - Implement proper error handling for each batch
   - Log errors and continue processing
   - Implement retry mechanisms for failed batches

3. **Resource Management**
   - Clean up temporary files
   - Close file handles properly
   - Release cloud storage connections
   - Monitor system resources

4. **Performance Optimization**
   - Use appropriate batch sizes
   - Implement parallel processing where possible
   - Monitor memory usage
   - Profile and optimize processing functions

## Troubleshooting

1. **Memory Issues**
   - Reduce batch size
   - Monitor memory usage
   - Implement garbage collection
   - Use memory profiling tools

2. **Performance Issues**
   - Profile processing functions
   - Optimize batch size
   - Check network latency
   - Monitor system resources

3. **Error Handling**
   - Check error logs
   - Implement retry logic
   - Verify data source access
   - Test with smaller datasets 