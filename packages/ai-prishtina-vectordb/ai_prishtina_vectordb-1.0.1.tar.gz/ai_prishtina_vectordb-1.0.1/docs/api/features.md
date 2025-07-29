# Feature Extraction API

The feature extraction system provides a flexible framework for extracting, processing, and storing features using ChromaDB. This document details the API components and their usage.

## FeatureConfig

Configuration class for feature extraction and processing.

### Parameters

- `normalize` (bool): Whether to normalize features (default: True)
- `dimensionality_reduction` (Optional[int]): Target dimension for feature reduction
- `feature_scaling` (bool): Whether to scale features (default: True)
- `cache_features` (bool): Whether to cache extracted features (default: True)
- `batch_size` (int): Batch size for processing (default: 100)
- `embedding_function` (str): Embedding function to use ("default", "openai", "sentence_transformer")
- `collection_name` (Optional[str]): Name of the Chroma collection
- `metadata` (Optional[Dict]): Default metadata for items
- `persist_directory` (Optional[str]): Directory for persistent storage
- `collection_metadata` (Optional[Dict]): Metadata for the collection
- `hnsw_config` (Optional[Dict]): HNSW index configuration
- `distance_function` (str): Distance function ("cosine", "l2", "ip")

### Example

```python
from ai_prishtina_vectordb.features import FeatureConfig

config = FeatureConfig(
    normalize=True,
    embedding_function="sentence_transformer",
    dimensionality_reduction=128,
    collection_name="my_collection",
    persist_directory="./chroma_db"
)
```

## FeatureExtractor

Base class for feature extraction.

### Methods

- `extract(data: Any) -> np.ndarray`: Extract features from input data
- `batch_extract(data_list: List[Any]) -> List[np.ndarray]`: Extract features from a batch of data

### Example

```python
from ai_prishtina_vectordb.features import FeatureExtractor

class CustomExtractor(FeatureExtractor):
    def extract(self, data: Any) -> np.ndarray:
        # Implement custom feature extraction
        pass
```

## TextFeatureExtractor

Extract features from text data using Chroma's embedding functions.

### Methods

- `extract(text: str) -> np.ndarray`: Extract features from text
- `batch_extract(texts: List[str]) -> List[np.ndarray]`: Extract features from a batch of texts

### Features

- Text embeddings using Chroma's embedding functions
- Text length
- Text complexity
- Feature normalization
- Feature caching

### Example

```python
from ai_prishtina_vectordb.features import TextFeatureExtractor

extractor = TextFeatureExtractor(config)
features = extractor.extract("Sample text")
```

## FeatureProcessor

Process and combine features from multiple extractors.

### Methods

- `process(data: Dict[str, Any]) -> np.ndarray`: Process features from multiple data types
- `add_to_collection(data: Dict[str, Any], id: str, metadata: Optional[Dict] = None, documents: Optional[List[str]] = None)`: Add processed features to collection
- `query_collection(query_data: Dict[str, Any], n_results: int = 5, where: Optional[Where] = None, where_document: Optional[WhereDocument] = None, include: Optional[List[str]] = None) -> QueryResult`: Query the collection
- `update_collection(ids: List[str], embeddings: Optional[List[List[float]]] = None, metadatas: Optional[List[Dict]] = None, documents: Optional[List[str]] = None)`: Update items in collection
- `delete_from_collection(ids: Optional[List[str]] = None, where: Optional[Where] = None, where_document: Optional[WhereDocument] = None)`: Delete items from collection
- `get_collection_stats() -> Dict[str, Any]`: Get collection statistics

### Example

```python
from ai_prishtina_vectordb.features import FeatureProcessor

processor = FeatureProcessor(config)

# Add to collection
processor.add_to_collection(
    data={"text": "Sample text"},
    id="doc1",
    metadata={"source": "example"}
)

# Query collection
results = processor.query_collection(
    query_data={"text": "Sample"},
    n_results=5,
    where={"source": "example"}
)

# Batch processing
features = processor.process({"text": "Batch text"})
```

## FeatureRegistry

Registry for managing feature extractors and processors.

### Methods

- `register_extractor(name: str, extractor: FeatureExtractor)`: Register a feature extractor
- `register_processor(name: str, processor: FeatureProcessor)`: Register a feature processor
- `get_extractor(name: str) -> FeatureExtractor`: Get a registered extractor
- `get_processor(name: str) -> FeatureProcessor`: Get a registered processor

### Example

```python
from ai_prishtina_vectordb.features import FeatureRegistry

registry = FeatureRegistry()
registry.register_extractor("text", TextFeatureExtractor(config))
extractor = registry.get_extractor("text")
```

## Error Handling

The feature extraction system uses custom exceptions for error handling:

```python
from ai_prishtina_vectordb.exceptions import FeatureError

try:
    processor.add_to_collection(data={"text": "sample"}, id="doc1")
except FeatureError as e:
    print(f"Error: {str(e)}")
```

## Best Practices

1. **Configuration**
   - Use persistent storage for production
   - Configure HNSW parameters based on data size
   - Choose appropriate distance function
   - Enable feature scaling for better results

2. **Feature Processing**
   - Use batch processing for large datasets
   - Enable caching for frequently accessed features
   - Apply dimensionality reduction for large feature sets
   - Normalize features for better results

3. **Collection Management**
   - Use meaningful collection names and metadata
   - Implement proper error handling
   - Monitor collection statistics
   - Use filters for efficient querying

4. **Performance**
   - Use appropriate batch sizes
   - Enable feature caching
   - Use persistent storage for large collections
   - Configure HNSW parameters for optimal search 