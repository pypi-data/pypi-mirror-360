import pytest
import os
import tempfile
from ..chroma_features import ChromaFeatures
from ..exceptions import DatabaseError, ValidationError

@pytest.fixture
async def chroma_features():
    """Fixture to create a ChromaFeatures instance with a temporary directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        features = ChromaFeatures(persist_directory=temp_dir)
        yield features

@pytest.mark.asyncio
async def test_create_collection_with_metadata(chroma_features):
    """Test creating a collection with metadata."""
    collection = await chroma_features.create_collection_with_metadata(
        name="test_collection",
        metadata={"description": "Test collection"},
        embedding_function="all-MiniLM-L6-v2"
    )
    assert collection.name == "test_collection"
    assert collection.metadata["description"] == "Test collection"

@pytest.mark.asyncio
async def test_get_collection_stats(chroma_features):
    """Test getting collection statistics."""
    # Create a collection first
    collection = await chroma_features.create_collection_with_metadata(
        name="test_collection",
        metadata={"description": "Test collection"}
    )
    
    # Add some test data
    await collection.add(
        documents=["Test document 1", "Test document 2"],
        metadatas=[{"type": "test"}, {"type": "test"}],
        ids=["1", "2"]
    )
    
    # Get stats
    stats = await chroma_features.get_collection_stats("test_collection")
    assert stats["total_documents"] == 2
    assert "metadata_distribution" in stats
    assert "embedding_dimension" in stats

@pytest.mark.asyncio
async def test_optimize_collection(chroma_features):
    """Test collection optimization."""
    # Create a collection first
    await chroma_features.create_collection_with_metadata(
        name="test_collection",
        metadata={"description": "Test collection"}
    )
    
    # Test optimization
    await chroma_features.optimize_collection(
        "test_collection",
        optimization_params={
            "hnsw_ef_construction": 100,
            "hnsw_m": 8,
            "hnsw_ef_search": 50
        }
    )

@pytest.mark.asyncio
async def test_backup_and_restore_collection(chroma_features):
    """Test backup and restore functionality."""
    # Create a collection with test data
    collection = await chroma_features.create_collection_with_metadata(
        name="test_collection",
        metadata={"description": "Test collection"}
    )
    
    await collection.add(
        documents=["Test document"],
        metadatas=[{"type": "test"}],
        ids=["1"]
    )
    
    # Create backup
    with tempfile.TemporaryDirectory() as backup_dir:
        await chroma_features.backup_collection("test_collection", backup_dir)
        
        # Verify backup file exists
        backup_file = os.path.join(backup_dir, "test_collection_backup.json")
        assert os.path.exists(backup_file)
        
        # Test restore
        await chroma_features.restore_collection(
            backup_file,
            "restored_collection"
        )
        
        # Verify restored collection
        restored = await chroma_features.client.get_collection("restored_collection")
        count = await restored.count()
        assert count == 1

@pytest.mark.asyncio
async def test_merge_collections(chroma_features):
    """Test merging collections."""
    # Create source collection
    source = await chroma_features.create_collection_with_metadata(
        name="source_collection",
        metadata={"description": "Source"}
    )
    
    await source.add(
        documents=["Source document"],
        metadatas=[{"type": "source"}],
        ids=["1"]
    )
    
    # Create target collection
    target = await chroma_features.create_collection_with_metadata(
        name="target_collection",
        metadata={"description": "Target"}
    )
    
    # Test merge
    await chroma_features.merge_collections(
        "source_collection",
        "target_collection",
        merge_strategy="append"
    )
    
    # Verify merge
    target = await chroma_features.client.get_collection("target_collection")
    count = await target.count()
    assert count == 1

@pytest.mark.asyncio
async def test_get_similarity_matrix(chroma_features):
    """Test getting similarity matrix."""
    # Create collection with test data
    collection = await chroma_features.create_collection_with_metadata(
        name="test_collection",
        metadata={"description": "Test collection"}
    )
    
    await collection.add(
        documents=["Test document 1", "Test document 2"],
        metadatas=[{"type": "test"}, {"type": "test"}],
        ids=["1", "2"]
    )
    
    # Get similarity matrix
    matrix = await chroma_features.get_similarity_matrix(
        "test_collection",
        ["1"],
        n_results=1
    )
    
    assert "1" in matrix
    assert len(matrix["1"]) == 1

@pytest.mark.asyncio
async def test_invalid_merge_strategy(chroma_features):
    """Test invalid merge strategy."""
    with pytest.raises(ValidationError):
        await chroma_features.merge_collections(
            "source_collection",
            "target_collection",
            merge_strategy="invalid"
        )

@pytest.mark.asyncio
async def test_nonexistent_collection(chroma_features):
    """Test operations on nonexistent collection."""
    with pytest.raises(DatabaseError):
        await chroma_features.get_collection_stats("nonexistent_collection") 