# Streaming Support

## Overview

The AIPrishtina VectorDB library provides robust streaming support for handling large datasets efficiently. This feature allows you to process data in batches without loading the entire dataset into memory, making it ideal for working with large files, cloud storage, and streaming data sources.

## Features

### 1. Batch Processing
- Configurable batch sizes
- Memory-efficient processing
- Support for all data source types
- Automatic batch management

### 2. Data Source Support
- Local files (CSV, JSON, TXT, etc.)
- Cloud storage (S3, GCS, Azure, MinIO)
- Pandas DataFrames
- Lists and dictionaries
- Binary data (numpy arrays, torch tensors, bytes)

### 3. Performance Optimizations
- Memory-efficient processing
- Parallel processing support
- Automatic resource cleanup
- Progress tracking

## Usage Examples

### Basic Streaming

```python
from aiprishtina_vectordb.data_sources import DataSource

# Initialize data source
source = DataSource()

# Stream from a large CSV file
for batch in source.stream_data(
    source="large_data.csv",
    text_column="content",
    metadata_columns=["source", "date"],
    batch_size=1000
):
    # Process each batch
    documents = batch["documents"]
    metadatas = batch["metadatas"]
    ids = batch["ids"]
    
    # Process the batch
    process_batch(documents, metadatas, ids)
```

### Cloud Storage Streaming

```python
# Stream from S3
for batch in source.stream_data(
    source="s3://my-bucket/data/",
    text_column="text",
    metadata_columns=["source", "bucket"],
    batch_size=500,
    aws_access_key_id="your_access_key",
    aws_secret_access_key="your_secret_key",
    region_name="your_region"
):
    process_batch(batch["documents"], batch["metadatas"], batch["ids"])

# Stream from MinIO
for batch in source.stream_data(
    source="minio://my-bucket/data/",
    text_column="text",
    metadata_columns=["source", "bucket"],
    batch_size=500,
    endpoint="your_minio_endpoint",
    access_key="your_access_key",
    secret_key="your_secret_key",
    secure=True
):
    process_batch(batch["documents"], batch["metadatas"], batch["ids"])
```

### DataFrame Streaming

```python
import pandas as pd
import numpy as np

# Create a large DataFrame
df = pd.DataFrame({
    "content": [f"Document {i}" for i in range(10000)],
    "source": ["local"] * 10000,
    "date": ["2024-01-01"] * 10000
})

# Stream from DataFrame
for batch in source.stream_data(
    source=df,
    text_column="content",
    metadata_columns=["source", "date"],
    batch_size=1000
):
    process_batch(batch["documents"], batch["metadatas"], batch["ids"])
```

### Binary Data Streaming

```python
import numpy as np
import torch

# Stream from numpy array
array_data = np.random.rand(10, 10)
for batch in source.stream_data(
    source=array_data,
    text_column=None,
    metadata_columns=["type"],
    batch_size=1
):
    process_batch(batch["documents"], batch["metadatas"], batch["ids"])

# Stream from torch tensor
tensor_data = torch.randn(10, 10)
for batch in source.stream_data(
    source=tensor_data,
    text_column=None,
    metadata_columns=["type"],
    batch_size=1
):
    process_batch(batch["documents"], batch["metadatas"], batch["ids"])
```

### List Streaming

```python
# Stream from list of dictionaries
data = [
    {"text": "Hello world", "source": "test"},
    {"text": "Welcome to AIPrishtina", "source": "test"}
]

for batch in source.stream_data(
    source=data,
    text_column="text",
    metadata_columns=["source"],
    batch_size=1
):
    process_batch(batch["documents"], batch["metadatas"], batch["ids"])
```

## API Reference

### DataSource.stream_data

```python
def stream_data(
    self,
    source: Union[str, Path, pd.DataFrame, List[Dict[str, Any]], bytes, np.ndarray, torch.Tensor],
    text_column: Optional[str] = None,
    metadata_columns: Optional[List[str]] = None,
    batch_size: int = 100,
    **kwargs
) -> Generator[Dict[str, Any], None, None]
```

#### Parameters

- `source`: Data source (file path, DataFrame, list of dicts, bytes, numpy array, torch tensor)
- `text_column`: Column name containing text to vectorize
- `metadata_columns`: Columns to include as metadata
- `batch_size`: Number of items to process in each batch
- `**kwargs`: Additional loading parameters
  - For S3: `aws_access_key_id`, `aws_secret_access_key`, `region_name`
  - For GCS: `project_id`, `credentials`
  - For Azure: `connection_string`
  - For MinIO: `endpoint`, `access_key`, `secret_key`, `secure`

#### Returns

- Generator yielding dictionaries containing:
  - `documents`: List of documents in the batch
  - `metadatas`: List of metadata dictionaries
  - `ids`: List of document IDs

#### Raises

- `ValueError`: If source type is not supported
- `DataSourceError`: If there's an error loading data
- `Exception`: For other processing errors

## Best Practices

1. **Batch Size Selection**
   - Choose batch size based on available memory
   - Larger batches for faster processing
   - Smaller batches for memory-constrained environments

2. **Error Handling**
   - Always wrap streaming in try-except blocks
   - Handle DataSourceError for source-specific issues
   - Implement proper cleanup in finally blocks

3. **Resource Management**
   - Close file handles and connections properly
   - Use context managers when possible
   - Monitor memory usage during streaming

4. **Performance Optimization**
   - Use appropriate batch sizes
   - Enable parallel processing when available
   - Monitor and adjust based on system resources

## Configuration

### Batch Processing Settings

```python
# Configure batch processing
source = DataSource(
    batch_size=1000,  # Default batch size
    max_retries=3,    # Number of retries for failed batches
    timeout=30        # Timeout for batch processing
)
```

### Cloud Storage Settings

```python
# Configure cloud storage streaming
source = DataSource(
    source_type="s3",
    aws_access_key_id="your_access_key",
    aws_secret_access_key="your_secret_key",
    region_name="us-west-2"
)
```

## Limitations

1. **Memory Usage**
   - Batch size affects memory consumption
   - Large objects may require smaller batch sizes
   - Consider available system memory

2. **Processing Time**
   - Batch processing adds overhead
   - Network latency affects cloud storage
   - Consider total processing time

3. **File Types**
   - Some file types require full loading
   - Binary files may need special handling
   - Consider file format limitations

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

## API Reference

### stream_data Method

```python
def stream_data(
    self,
    source: Union[str, Path, pd.DataFrame, List[Dict[str, Any]], bytes, np.ndarray, torch.Tensor],
    text_column: Optional[str] = None,
    metadata_columns: Optional[List[str]] = None,
    batch_size: int = 1000,
    **kwargs
) -> Generator[Dict[str, Any], None, None]
```

#### Parameters

- `source`: Data source (file path, DataFrame, list of dicts, bytes, numpy array, torch tensor)
- `text_column`: Column name containing text to vectorize
- `metadata_columns`: Columns to include as metadata
- `batch_size`: Number of items to process in each batch
- `**kwargs`: Additional loading parameters

#### Returns

- Generator yielding dictionaries containing:
  - `documents`: List of documents in the batch
  - `metadatas`: List of metadata dictionaries
  - `ids`: List of document IDs

#### Raises

- `ValueError`: If source type is not supported
- `DataSourceError`: If there's an error loading data
- `Exception`: For other processing errors 