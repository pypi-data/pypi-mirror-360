"""Tests for the Database class."""

import pytest
import numpy as np
from pathlib import Path
import tempfile
import shutil
from ai_prishtina_vectordb.database import Database
from ai_prishtina_vectordb.config import DatabaseConfig
from ai_prishtina_vectordb.exceptions import ValidationError

@pytest.fixture
async def database():
    """Create a test database instance."""
    temp_dir = tempfile.mkdtemp()
    db = Database(
        collection_name="test_collection",
        persist_directory=temp_dir
    )
    await db.initialize()
    try:
        return db
    finally:
        await db.close()
        shutil.rmtree(temp_dir)

@pytest.mark.skip(reason="Database tests temporarily disabled")
@pytest.mark.asyncio
async def test_database_initialization(database):
    """Test database initialization."""
    assert database is not None
    assert database.collection is not None
    assert database.collection.name == "test_collection"

@pytest.mark.skip(reason="Database tests temporarily disabled")
@pytest.mark.asyncio
async def test_add_documents(database):
    """Test adding documents to the database."""
    documents = ["Test document 1", "Test document 2"]
    metadatas = [{"source": "test1"}, {"source": "test2"}]
    
    ids = await database.add_documents(documents, metadatas)
    assert len(ids) == 2
    assert all(isinstance(id, str) for id in ids)

@pytest.mark.skip(reason="Database tests temporarily disabled")
@pytest.mark.asyncio
async def test_query_documents(database):
    """Test querying documents from the database."""
    # First add some documents
    documents = ["Test document 1", "Test document 2"]
    metadatas = [{"source": "test1"}, {"source": "test2"}]
    await database.add_documents(documents, metadatas)
    
    # Query the documents
    results = await database.query_documents("Test document 1", n_results=1)
    assert len(results) > 0
    assert "Test document 1" in results[0]

@pytest.mark.skip(reason="Database tests temporarily disabled")
@pytest.mark.asyncio
async def test_delete_documents(database):
    """Test deleting documents from the database."""
    # First add some documents
    documents = ["Test document 1", "Test document 2"]
    metadatas = [{"source": "test1"}, {"source": "test2"}]
    ids = await database.add_documents(documents, metadatas)
    
    # Delete one document
    await database.delete_documents([ids[0]])
    
    # Verify deletion
    results = await database.query_documents("Test document 1", n_results=1)
    assert len(results) == 0

@pytest.mark.skip(reason="Database tests temporarily disabled")
@pytest.mark.asyncio
async def test_update_documents(database):
    """Test updating documents in the database."""
    # First add a document
    documents = ["Test document 1"]
    metadatas = [{"source": "test1"}]
    ids = await database.add_documents(documents, metadatas)
    
    # Update the document
    new_documents = ["Updated document 1"]
    new_metadatas = [{"source": "test1_updated"}]
    await database.update_documents(ids, new_documents, new_metadatas)
    
    # Verify update
    results = await database.query_documents("Updated document 1", n_results=1)
    assert len(results) > 0
    assert "Updated document 1" in results[0]

@pytest.mark.skip(reason="Database tests temporarily disabled")
@pytest.mark.asyncio
async def test_add_embeddings(database):
    """Test adding embeddings to the database."""
    embeddings = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
    metadatas = [{"source": "test1"}, {"source": "test2"}]
    documents = ["Test document 1", "Test document 2"]
    
    ids = await database.add_embeddings(embeddings, metadatas, documents)
    assert len(ids) == 2
    assert all(isinstance(id, str) for id in ids)

@pytest.mark.skip(reason="Database tests temporarily disabled")
@pytest.mark.asyncio
async def test_query_by_text(database):
    """Test querying by text."""
    # First add some documents
    documents = ["Test document 1", "Test document 2"]
    metadatas = [{"source": "test1"}, {"source": "test2"}]
    await database.add_documents(documents, metadatas)
    
    # Query by text
    results = await database.query_by_text("Test document 1", n_results=1)
    assert len(results) > 0
    assert "Test document 1" in results[0]

@pytest.mark.skip(reason="Database tests temporarily disabled")
@pytest.mark.asyncio
async def test_query_by_embeddings(database):
    """Test querying by embeddings."""
    # First add some embeddings
    embeddings = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
    metadatas = [{"source": "test1"}, {"source": "test2"}]
    documents = ["Test document 1", "Test document 2"]
    await database.add_embeddings(embeddings, metadatas, documents)
    
    # Query by embedding
    query_embedding = [1.0, 2.0, 3.0]
    results = await database.query_by_embeddings([query_embedding], n_results=1)
    assert len(results) > 0
    assert "Test document 1" in results[0]

@pytest.mark.skip(reason="Database tests temporarily disabled")
@pytest.mark.asyncio
async def test_delete_by_ids(database):
    """Test deleting vectors by IDs."""
    # First add some documents
    documents = ["Test document 1", "Test document 2"]
    metadatas = [{"source": "test1"}, {"source": "test2"}]
    ids = await database.add_documents(documents, metadatas)
    
    # Delete by IDs
    await database.delete_by_ids([ids[0]])
    
    # Verify deletion
    results = await database.query_documents("Test document 1", n_results=1)
    assert len(results) == 0

@pytest.mark.skip(reason="Database tests temporarily disabled")
@pytest.mark.asyncio
async def test_delete_by_where(database):
    """Test deleting vectors by where clause."""
    # First add some documents
    documents = ["Test document 1", "Test document 2"]
    metadatas = [{"source": "test1"}, {"source": "test2"}]
    await database.add_documents(documents, metadatas)
    
    # Delete by where clause
    await database.delete_by_where({"source": "test1"})
    
    # Verify deletion
    results = await database.query_documents("Test document 1", n_results=1)
    assert len(results) == 0

@pytest.mark.skip(reason="Database tests temporarily disabled")
@pytest.mark.asyncio
async def test_update(database):
    """Test updating vectors."""
    # First add some documents
    documents = ["Test document 1", "Test document 2"]
    metadatas = [{"source": "test1"}, {"source": "test2"}]
    ids = await database.add_documents(documents, metadatas)
    
    # Update vectors
    new_documents = ["Updated document 1", "Updated document 2"]
    new_metadatas = [{"source": "test1_updated"}, {"source": "test2_updated"}]
    await database.update(ids, new_documents, new_metadatas)
    
    # Verify update
    results = await database.query_documents("Updated document 1", n_results=1)
    assert len(results) > 0
    assert "Updated document 1" in results[0]

@pytest.mark.skip(reason="Database tests temporarily disabled")
@pytest.mark.asyncio
async def test_create_index(database):
    """Test creating an index."""
    # First add some documents
    documents = ["Test document 1", "Test document 2"]
    metadatas = [{"source": "test1"}, {"source": "test2"}]
    await database.add_documents(documents, metadatas)
    
    # Create index
    await database.create_index()
    
    # Verify index creation
    assert database.collection is not None
    assert database.collection.count() > 0

@pytest.mark.skip(reason="Database tests temporarily disabled")
@pytest.mark.asyncio
async def test_invalid_operations(database):
    """Test invalid operations."""
    # Test invalid document addition
    with pytest.raises(ValueError):
        await database.add_documents([], [])
    
    # Test invalid query
    with pytest.raises(ValueError):
        await database.query_documents("", n_results=0)
    
    # Test invalid deletion
    with pytest.raises(ValueError):
        await database.delete_documents([]) 