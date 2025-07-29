# Data Sources

## Overview

The AIPrishtina VectorDB library provides comprehensive support for various data sources, including local files, cloud storage, and in-memory data structures. This document outlines the supported data sources and their usage.

## Supported Data Sources

### 1. Local Files
- Text files (.txt, .md)
- JSON files (.json)
- CSV files (.csv)
- Excel files (.xls, .xlsx)
- Word documents (.doc, .docx)
- PDF files (.pdf)
- Image files (.jpg, .png, .jpeg)
- Audio files (.wav, .mp3)
- Video files (.mp4, .avi)

### 2. Cloud Storage
- Amazon S3
- Google Cloud Storage
- Azure Blob Storage
- MinIO

### 3. In-Memory Data
- Pandas DataFrames
- Lists and dictionaries
- Binary data (numpy arrays, torch tensors, bytes)

## Usage Examples

### Local File Loading

```python
from ai_prishtina_vectordb.data_sources import DataSource

# Initialize data source
source = DataSource()

# Load from text file
data = source.load_data(
    source="data.txt",
    text_column=None,
    metadata_columns=["source"]
)

# Load from CSV file
data = source.load_data(
    source="data.csv",
    text_column="content",
    metadata_columns=["source", "date"]
)

# Load from JSON file
data = source.load_data(
    source="data.json",
    text_column="text",
    metadata_columns=["source", "category"]
)
```

### Cloud Storage Loading

```python
# Load from S3
data = source.load_data(
    source="s3://my-bucket/data/",
    text_column="text",
    metadata_columns=["source", "bucket"],
    aws_access_key_id="your_access_key",
    aws_secret_access_key="your_secret_key",
    region_name="your_region"
)

# Load from MinIO
data = source.load_data(
    source="minio://my-bucket/data/",
    text_column="text",
    metadata_columns=["source", "bucket"],
    endpoint="your_minio_endpoint",
    access_key="your_access_key",
    secret_key="your_secret_key",
    secure=True
)
```

### In-Memory Data Loading

```python
import pandas as pd
import numpy as np
import torch

# Load from DataFrame
df = pd.DataFrame({
    "content": ["Document 1", "Document 2"],
    "source": ["local", "local"],
    "date": ["2024-01-01", "2024-01-02"]
})

data = source.load_data(
    source=df,
    text_column="content",
    metadata_columns=["source", "date"]
)

# Load from list of dictionaries
data_list = [
    {"text": "Hello world", "source": "test"},
    {"text": "Welcome to AIPrishtina", "source": "test"}
]

data = source.load_data(
    source=data_list,
    text_column="text",
    metadata_columns=["source"]
)

# Load from binary data
array_data = np.random.rand(10, 10)
data = source.load_data(
    source=array_data,
    text_column=None,
    metadata_columns=["type"]
)

tensor_data = torch.randn(10, 10)
data = source.load_data(
    source=tensor_data,
    text_column=None,
    metadata_columns=["type"]
)
```

## API Reference

### DataSource

```python
class DataSource:
    def __init__(
        self,
        source_type: str = "text",
        embedding_function: Optional[Any] = None,
        **kwargs
    ):
        """
        Initialize the data source handler.
        
        Args:
            source_type: Type of data source ('text', 'json', 'csv', 'excel', 'word', 'pdf', 'pandas', 'image', 'audio', 'video', 'url', 's3', 'gcs', 'azure', 'sql', 'custom', 'binary')
            embedding_function: Optional custom embedding function
            **kwargs: Additional configuration parameters
        """
```

### DataSource.load_data

```python
def load_data(
    self,
    source: Union[str, Path, pd.DataFrame, List[Dict[str, Any]], bytes, np.ndarray, torch.Tensor],
    text_column: Optional[str] = None,
    metadata_columns: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Load data from various sources.
    
    Args:
        source: Data source (file path, DataFrame, list of dicts, bytes, numpy array, torch tensor)
        text_column: Column name containing text to vectorize
        metadata_columns: Columns to include as metadata
        **kwargs: Additional loading parameters
        
    Returns:
        Dict containing documents, metadatas, and ids
    """
```

## Best Practices

1. **File Type Detection**
   - Use appropriate file extensions
   - Handle binary files properly
   - Validate file formats before processing

2. **Error Handling**
   - Implement proper error handling
   - Handle missing files gracefully
   - Validate data formats

3. **Resource Management**
   - Close file handles properly
   - Clean up temporary files
   - Release cloud storage connections

4. **Performance Optimization**
   - Use appropriate batch sizes
   - Enable parallel processing when available
   - Monitor memory usage

## Configuration

### Cloud Storage Configuration

#### Amazon S3
```python
source = DataSource(
    source_type="s3",
    aws_access_key_id="your_access_key",
    aws_secret_access_key="your_secret_key",
    region_name="your_region"
)
```

#### Google Cloud Storage
```python
source = DataSource(
    source_type="gcs",
    project_id="your_project_id",
    credentials="your_credentials"
)
```

#### Azure Blob Storage
```python
source = DataSource(
    source_type="azure",
    connection_string="your_connection_string"
)
```

#### MinIO
```python
source = DataSource(
    source_type="minio",
    endpoint="your_endpoint",
    access_key="your_access_key",
    secret_key="your_secret_key",
    secure=True
)
```

## Class: DataSource

Base class for handling different types of data sources.

### Initialization

```python
DataSource(
    source_type: str,
    embedding_function: Optional[Callable] = None,
    preprocessing_steps: Optional[List[str]] = None,
    **kwargs
)
```

#### Parameters

- `source_type` (str): Type of data source
- `embedding_function` (Callable, optional): Custom embedding function
- `preprocessing_steps` (List[str], optional): List of preprocessing steps
- `**kwargs`: Additional source-specific parameters

### Methods

#### load_data

Load and process data from a source.

```python
load_data(
    source: Union[str, Path, DataFrame, np.ndarray],
    metadata_columns: Optional[List[str]] = None,
    **kwargs
) -> Dict
```

##### Parameters

- `source`: Data source (file path, DataFrame, or array)
- `metadata_columns` (List[str], optional): Columns to include as metadata
- `**kwargs`: Additional source-specific parameters

##### Returns

- Dict containing:
  - `documents`: List of processed documents
  - `metadatas`: List of metadata dictionaries
  - `ids`: List of document IDs

##### Example

```python
source = DataSource(source_type="text")
data = source.load_data(
    source="data.txt",
    metadata_columns=["author", "date"]
)
```

#### preprocess

Preprocess the data.

```python
preprocess(
    data: Union[str, List[str], np.ndarray],
    steps: Optional[List[str]] = None
) -> Union[str, List[str], np.ndarray]
```

##### Parameters

- `data`: Input data to preprocess
- `steps` (List[str], optional): List of preprocessing steps

##### Returns

- Preprocessed data

##### Example

```python
processed_data = source.preprocess(
    data=["raw text 1", "raw text 2"],
    steps=["clean", "normalize"]
)
```

#### validate

Validate the data source and its contents.

```python
validate(
    source: Union[str, Path, DataFrame, np.ndarray],
    **kwargs
) -> bool
```

##### Parameters

- `source`: Data source to validate
- `**kwargs`: Additional validation parameters

##### Returns

- bool: True if validation passes, False otherwise

##### Example

```python
is_valid = source.validate(
    source="data.txt",
    required_columns=["text", "metadata"]
)
```

### Properties

#### source_type

Get the type of data source.

```python
@property
def source_type(self) -> str
```

#### embedding_function

Get the embedding function.

```python
@property
def embedding_function(self) -> Optional[Callable]
```

## Specialized Data Sources

### TextSource

Handles text data sources.

```python
TextSource(
    embedding_function: Optional[Callable] = None,
    preprocessing_steps: Optional[List[str]] = None,
    **kwargs
)
```

### ImageSource

Handles image data sources.

```python
ImageSource(
    embedding_function: Optional[Callable] = None,
    preprocessing_steps: Optional[List[str]] = None,
    **kwargs
)
```

### AudioSource

Handles audio data sources.

```python
AudioSource(
    embedding_function: Optional[Callable] = None,
    preprocessing_steps: Optional[List[str]] = None,
    **kwargs
)
```

### VideoSource

Handles video data sources.

```python
VideoSource(
    embedding_function: Optional[Callable] = None,
    preprocessing_steps: Optional[List[str]] = None,
    **kwargs
)
```

### CustomSource

Handles custom data sources.

```python
CustomSource(
    embedding_function: Callable,
    preprocessing_steps: Optional[List[str]] = None,
    **kwargs
)
```

## Error Handling

The classes raise the following exceptions:

- `InvalidSourceError`: When the data source is invalid
- `ProcessingError`: When data processing fails
- `ValidationError`: When data validation fails
- `EmbeddingError`: When embedding generation fails

## Example Usage

```python
from ai_prishtina_vectordb import DataSource, TextSource, ImageSource

# Text data source
text_source = TextSource(
    preprocessing_steps=["clean", "normalize"]
)
text_data = text_source.load_data(
    source="documents.txt",
    metadata_columns=["author", "date"]
)

# Image data source
image_source = ImageSource(
    preprocessing_steps=["resize", "normalize"]
)
image_data = image_source.load_data(
    source="images/",
    metadata_columns=["category", "tags"]
)

# Custom data source
class CustomEmbeddingFunction:
    def __call__(self, data):
        # Custom embedding logic
        return embeddings

custom_source = DataSource(
    source_type="custom",
    embedding_function=CustomEmbeddingFunction()
)
custom_data = custom_source.load_data(
    source=my_custom_data,
    metadata_columns=["field1", "field2"]
)

import chromadb

client = chromadb.PersistentClient(path="/tmp/chroma-test")  # or your desired path
# or for in-memory:
client = chromadb.EphemeralClient() 