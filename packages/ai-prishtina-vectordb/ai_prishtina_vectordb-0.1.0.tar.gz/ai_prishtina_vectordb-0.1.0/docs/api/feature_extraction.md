# Feature Extraction Examples

This document provides examples of using the feature extraction system with Chroma integration.

## Basic Text Feature Extraction

```python
from ai_prishtina_vectordb.features import FeatureConfig, TextFeatureExtractor

# Configure feature extraction
config = FeatureConfig(
    normalize=True,
    embedding_function="sentence_transformer",
    dimensionality_reduction=128
)

# Create extractor
extractor = TextFeatureExtractor(config)

# Extract features from text
text = "This is a sample text for feature extraction"
features = extractor.extract(text)
print(f"Extracted features shape: {features.shape}")
```

## Using Feature Processor with Chroma Collection

```python
from ai_prishtina_vectordb.features import FeatureConfig, FeatureProcessor

# Configure processor with Chroma collection
config = FeatureConfig(
    collection_name="my_collection",
    persist_directory="./chroma_db",
    collection_metadata={"description": "My text collection"},
    hnsw_config={"M": 16, "ef_construction": 100},
    distance_function="cosine"
)

# Create processor
processor = FeatureProcessor(config)

# Add data to collection
data = {
    "text": "This is a sample document",
    "metadata": {"source": "example", "category": "test"}
}
processor.add_to_collection(
    data=data,
    id="doc1",
    metadata={"source": "example"},
    documents=["This is a sample document"]
)

# Query collection with filters
results = processor.query_collection(
    query_data={"text": "sample document"},
    n_results=5,
    where={"source": "example"},
    where_document={"$contains": "sample"},
    include=["documents", "metadatas", "distances"]
)
print(f"Query results: {results}")

# Update collection items
processor.update_collection(
    ids=["doc1"],
    metadatas=[{"source": "updated", "category": "test"}],
    documents=["Updated document content"]
)

# Delete items with filters
processor.delete_from_collection(
    where={"category": "test"}
)

# Get collection statistics
stats = processor.get_collection_stats()
print(f"Collection stats: {stats}")
```

## Batch Processing

```python
from ai_prishtina_vectordb.features import FeatureConfig, TextFeatureExtractor

# Configure extractor
config = FeatureConfig(
    normalize=True,
    batch_size=100
)

# Create extractor
extractor = TextFeatureExtractor(config)

# Process batch of texts
texts = [
    "First document",
    "Second document",
    "Third document"
]
features = extractor.batch_extract(texts)
print(f"Batch features shape: {len(features)}")
```

## Using Feature Registry

```python
from ai_prishtina_vectordb.features import (
    FeatureConfig,
    TextFeatureExtractor,
    FeatureProcessor,
    FeatureRegistry
)

# Create registry
registry = FeatureRegistry()

# Register extractors
text_config = FeatureConfig(embedding_function="sentence_transformer")
registry.register_extractor("text", TextFeatureExtractor(text_config))

# Register processors
processor_config = FeatureConfig(
    collection_name="my_collection",
    persist_directory="./chroma_db"
)
registry.register_processor("default", FeatureProcessor(processor_config))

# Use registered components
extractor = registry.get_extractor("text")
processor = registry.get_processor("default")

# Process and store features
text = "Sample text for processing"
features = extractor.extract(text)
processor.add_to_collection(
    data={"text": text},
    id="doc1",
    metadata={"source": "registry_example"}
)
```

## Advanced Usage with Dimensionality Reduction

```python
from ai_prishtina_vectordb.features import FeatureConfig, FeatureProcessor

# Configure processor with dimensionality reduction
config = FeatureConfig(
    collection_name="reduced_collection",
    dimensionality_reduction=64,
    feature_scaling=True,
    persist_directory="./chroma_db"
)

# Create processor
processor = FeatureProcessor(config)

# Add data with reduced dimensions
data = {
    "text": "This is a long text that will be reduced to 64 dimensions",
    "metadata": {"source": "advanced_example"}
}
processor.add_to_collection(
    data=data,
    id="doc1",
    metadata={"source": "advanced_example"}
)

# Query with reduced dimensions
results = processor.query_collection(
    query_data={"text": "long text"},
    n_results=5,
    include=["documents", "distances"]
)
print(f"Query results with reduced dimensions: {results}")
```

## Error Handling

```python
from ai_prishtina_vectordb.features import FeatureConfig, FeatureProcessor
from ai_prishtina_vectordb.exceptions import FeatureError

# Configure processor without collection
config = FeatureConfig()

# Create processor
processor = FeatureProcessor(config)

try:
    # This will raise FeatureError
    processor.add_to_collection(
        data={"text": "sample"},
        id="doc1"
    )
except FeatureError as e:
    print(f"Error: {str(e)}")
```

## Best Practices

1. **Configuration**:
   - Use persistent storage for production
   - Configure HNSW parameters based on your data size
   - Choose appropriate distance function for your use case
   - Enable feature scaling for better results

2. **Collection Management**:
   - Use meaningful collection names and metadata
   - Implement proper error handling
   - Monitor collection statistics
   - Use filters for efficient querying

3. **Feature Processing**:
   - Use batch processing for large datasets
   - Enable caching for frequently accessed features
   - Apply dimensionality reduction for large feature sets
   - Normalize features for better results

4. **Performance Optimization**:
   - Use appropriate batch sizes
   - Enable feature caching
   - Use persistent storage for large collections
   - Configure HNSW parameters for optimal search 