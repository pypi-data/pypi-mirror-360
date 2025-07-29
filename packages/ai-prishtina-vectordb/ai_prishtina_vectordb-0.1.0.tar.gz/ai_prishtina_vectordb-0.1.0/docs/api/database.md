# VectorDatabase API Reference

## Class: VectorDatabase

The main interface for vector database operations.

### Initialization

```python
VectorDatabase(
    collection_name: str,
    persist_directory: Optional[str] = None,
    embedding_function: Optional[Callable] = None,
    collection_metadata: Optional[Dict] = None
)
```

#### Parameters

- `collection_name` (str): Name of the collection to create or connect to
- `persist_directory` (str, optional): Directory to persist the database
- `embedding_function` (Callable, optional): Custom embedding function
- `collection_metadata` (Dict, optional): Metadata for the collection

### Methods

#### add

Add documents to the database.

```python
add(
    documents: List[str],
    metadatas: Optional[List[Dict]] = None,
    ids: Optional[List[str]] = None
) -> None
```

##### Parameters

- `documents` (List[str]): List of documents to add
- `metadatas` (List[Dict], optional): List of metadata dictionaries
- `ids` (List[str], optional): List of document IDs

##### Example

```python
db.add(
    documents=["Document 1", "Document 2"],
    metadatas=[{"source": "file1"}, {"source": "file2"}],
    ids=["doc1", "doc2"]
)
```

#### add_from_source

Add documents from a data source.

```python
add_from_source(
    source: Union[str, Path, DataFrame, np.ndarray],
    source_type: str,
    text_column: Optional[str] = None,
    metadata_columns: Optional[List[str]] = None,
    **kwargs
) -> None
```

##### Parameters

- `source`: Data source (file path, DataFrame, or array)
- `source_type` (str): Type of data source
- `text_column` (str, optional): Column containing text data
- `metadata_columns` (List[str], optional): Columns to include as metadata
- `**kwargs`: Additional source-specific parameters

##### Example

```python
db.add_from_source(
    source="data.json",
    source_type="json",
    text_column="content",
    metadata_columns=["author", "date"]
)
```

#### query

Query the database for similar documents.

```python
query(
    query_texts: Optional[List[str]] = None,
    query_embeddings: Optional[np.ndarray] = None,
    n_results: int = 10,
    where: Optional[Dict] = None,
    where_document: Optional[Dict] = None
) -> Dict
```

##### Parameters

- `query_texts` (List[str], optional): List of query texts
- `query_embeddings` (np.ndarray, optional): Pre-computed query embeddings
- `n_results` (int): Number of results to return
- `where` (Dict, optional): Metadata filter
- `where_document` (Dict, optional): Document content filter

##### Returns

- Dict containing:
  - `documents`: List of matching documents
  - `metadatas`: List of document metadata
  - `distances`: List of similarity distances
  - `ids`: List of document IDs

##### Example

```python
results = db.query(
    query_texts=["What is machine learning?"],
    n_results=5,
    where={"category": "ml"}
)
```

#### create_index

Create an index for efficient similarity search.

```python
create_index(
    index_type: str = "hnsw",
    **kwargs
) -> None
```

##### Parameters

- `index_type` (str): Type of index to create
- `**kwargs`: Index-specific parameters

##### Example

```python
db.create_index(
    index_type="hnsw",
    M=16,
    ef_construction=100
)
```

#### delete

Delete documents from the database.

```python
delete(
    ids: Optional[List[str]] = None,
    where: Optional[Dict] = None,
    where_document: Optional[Dict] = None
) -> None
```

##### Parameters

- `ids` (List[str], optional): List of document IDs to delete
- `where` (Dict, optional): Metadata filter for deletion
- `where_document` (Dict, optional): Document content filter for deletion

##### Example

```python
db.delete(
    where={"category": "deprecated"}
)
```

#### update

Update documents in the database.

```python
update(
    ids: List[str],
    documents: Optional[List[str]] = None,
    metadatas: Optional[List[Dict]] = None
) -> None
```

##### Parameters

- `ids` (List[str]): List of document IDs to update
- `documents` (List[str], optional): New document contents
- `metadatas` (List[Dict], optional): New metadata

##### Example

```python
db.update(
    ids=["doc1", "doc2"],
    metadatas=[{"status": "updated"}, {"status": "updated"}]
)
```

### Properties

#### collection_name

Get the name of the current collection.

```python
@property
def collection_name(self) -> str
```

#### collection_metadata

Get the metadata of the current collection.

```python
@property
def collection_metadata(self) -> Dict
```

### Error Handling

The class raises the following exceptions:

- `CollectionNotFoundError`: When the specified collection doesn't exist
- `InvalidDataError`: When input data is invalid
- `QueryError`: When a query operation fails
- `IndexError`: When index operations fail

### Example Usage

```python
from ai_prishtina_vectordb import VectorDatabase

# Initialize database
db = VectorDatabase(
    collection_name="my_collection",
    persist_directory="./data"
)

# Add documents
db.add(
    documents=["Document 1", "Document 2"],
    metadatas=[{"category": "A"}, {"category": "B"}]
)

# Query documents
results = db.query(
    query_texts=["Example query"],
    n_results=5,
    where={"category": "A"}
)

# Update documents
db.update(
    ids=["doc1"],
    metadatas=[{"status": "updated"}]
)

# Delete documents
db.delete(where={"category": "B"})
``` 