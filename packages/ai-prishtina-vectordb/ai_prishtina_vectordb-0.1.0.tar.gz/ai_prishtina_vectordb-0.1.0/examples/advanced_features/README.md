# Advanced Features Example

This example demonstrates advanced features and capabilities of AIPrishtina VectorDB.

## Features
- Advanced indexing and search capabilities
- Enhanced embedding models and fine-tuning
- Advanced caching strategies
- Performance optimizations
- Advanced query features

## Directory Structure
```
advanced_features/
├── data/           # Sample data files
├── logs/           # Log files
└── main.py         # Main example code
```

## Usage
1. Run the example:
```bash
python main.py
```

2. Check the logs in `logs/advanced_features.log` for detailed execution information.

## Advanced Features

### Indexing
- HNSW (Hierarchical Navigable Small World) index for approximate nearest neighbor search
- IVF (Inverted File) index for clustering-based search
- Configurable index parameters for performance tuning

### Search Capabilities
- Hybrid search combining vector and keyword search
- Faceted search with multiple dimensions
- Range-based search with numeric filters
- Metadata filtering and sorting

### Performance Optimizations
- Parallel batch processing with ThreadPoolExecutor
- Configurable batch sizes and worker counts
- Progress tracking and logging
- Error handling and recovery

### Sample Data
The example creates sample documents with rich metadata including:
- Categories
- Dates
- Authors
- Tags
- View counts
- Ratings

## Advanced Usage

### Custom Index Configuration
```python
db = AdvancedVectorDB(
    collection_name="my_collection",
    index_type="hnsw",
    M=16,  # Number of connections per element
    ef_construction=100,  # Size of dynamic candidate list
    ef_search=50  # Size of dynamic candidate list during search
)
```

### Hybrid Search
```python
results = db.hybrid_search(
    query="How is technology changing healthcare?",
    n_results=3
)
```

### Faceted Search
```python
facets = {
    "category": ["Technology", "Science", "Environment"],
    "tags": ["AI", "Healthcare", "ML"]
}
results = db.faceted_search(
    query="technology",
    facets=facets,
    n_results=2
)
```

### Range Search
```python
range_filters = {
    "views": {"min": 500, "max": 1500},
    "rating": {"min": 4.0, "max": 5.0}
}
results = db.range_search(
    query="technology",
    range_filters=range_filters,
    n_results=3
)
```

### Batch Processing
```python
db.batch_process(
    documents=documents,
    metadatas=metadatas,
    batch_size=100,
    max_workers=4
)
``` 