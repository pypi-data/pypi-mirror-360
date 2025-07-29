# AIPrishtina VectorDB

A powerful vector database library for efficient similarity search and data management.

## Features

### 1. Data Source Support
- Local files (CSV, JSON, TXT, etc.)
- Cloud storage (S3, GCS, Azure, MinIO)
- Pandas DataFrames
- Lists and dictionaries
- Binary data (numpy arrays, torch tensors, bytes)

### 2. Streaming Support
- Memory-efficient batch processing
- Configurable batch sizes
- Support for all data source types
- Automatic resource management

### 3. Vector Operations
- Efficient similarity search
- Custom embedding functions
- Batch vector operations
- Vector normalization

### 4. Cloud Storage Integration
- Amazon S3
- Google Cloud Storage
- Azure Blob Storage
- MinIO

## Quick Start

### Installation

```bash
pip install ai-prishtina-vectordb
```

### Basic Usage

```python
from ai_prishtina_vectordb.data_sources import DataSource
from ai_prishtina_vectordb.database import Database

# Initialize data source
source = DataSource()

# Load data
data = source.load_data(
    source="data.csv",
    text_column="content",
    metadata_columns=["source", "date"]
)

# Initialize database
db = Database()

# Add documents
db.add_documents(
    documents=data["documents"],
    metadatas=data["metadatas"],
    ids=data["ids"]
)

# Query similar documents
results = db.query(
    query_texts=["example query"],
    n_results=5
)
```

### Streaming Example

```python
# Stream from a large CSV file
for batch in source.stream_data(
    source="large_data.csv",
    text_column="content",
    metadata_columns=["source", "date"],
    batch_size=1000
):
    # Process each batch
    db.add_documents(
        documents=batch["documents"],
        metadatas=batch["metadatas"],
        ids=batch["ids"]
    )
```

### Cloud Storage Example

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
    db.add_documents(
        documents=batch["documents"],
        metadatas=batch["metadatas"],
        ids=batch["ids"]
    )
```

## Documentation

- [Data Sources](data_sources.md)
- [Streaming](streaming.md)
- [Database Operations](database.md)
- [Feature Extraction](feature_extraction.md)
- [Features](features.md)

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details. 