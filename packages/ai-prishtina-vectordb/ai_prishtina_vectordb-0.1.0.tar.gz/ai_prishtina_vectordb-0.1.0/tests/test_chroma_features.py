"""Tests for ChromaDB features functionality."""

import pytest
import tempfile
import shutil
import os
from pathlib import Path
import numpy as np
from unittest.mock import MagicMock, patch
from ai_prishtina_vectordb.chroma_features import ChromaFeatures
from ai_prishtina_vectordb.exceptions import FeatureError
import chromadb


@pytest.fixture(scope="function")
def temp_dir():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def chroma_features(temp_dir):
    """Create ChromaFeatures instance for testing."""
    return ChromaFeatures(persist_directory=temp_dir)


@pytest.fixture
def sample_collection_data():
    """Sample data for collection operations."""
    return {
        'documents': [
            "This is a test document about machine learning.",
            "Vector databases enable similarity search.",
            "ChromaDB is a powerful vector database.",
            "AI applications use vector embeddings.",
            "Natural language processing with vectors."
        ],
        'metadatas': [
            {"category": "ml", "type": "test"},
            {"category": "database", "type": "test"},
            {"category": "database", "type": "test"},
            {"category": "ai", "type": "test"},
            {"category": "nlp", "type": "test"}
        ],
        'ids': ["doc1", "doc2", "doc3", "doc4", "doc5"]
    }


class TestChromaFeatures:
    """Test cases for ChromaFeatures."""

    def test_init(self, temp_dir):
        """Test ChromaFeatures initialization."""
        features = ChromaFeatures(persist_directory=temp_dir)
        
        assert features.persist_directory == temp_dir
        assert features.client is not None
        assert hasattr(features, 'logger')

    def test_init_with_client(self):
        """Test initialization with existing client."""
        mock_client = MagicMock()
        features = ChromaFeatures(client=mock_client)
        
        assert features.client == mock_client

    def test_create_collection_success(self, chroma_features):
        """Test successful collection creation."""
        collection_name = "test_collection"
        
        collection = chroma_features.create_collection(
            name=collection_name,
            metadata={"description": "Test collection"}
        )
        
        assert collection is not None
        assert collection.name == collection_name

    def test_create_collection_already_exists(self, chroma_features):
        """Test creating collection that already exists."""
        collection_name = "existing_collection"
        
        # Create collection first time
        chroma_features.create_collection(name=collection_name)
        
        # Try to create again - should handle gracefully
        collection = chroma_features.create_collection(name=collection_name)
        assert collection is not None

    def test_get_collection_success(self, chroma_features):
        """Test getting existing collection."""
        collection_name = "get_test_collection"
        
        # Create collection first
        chroma_features.create_collection(name=collection_name)
        
        # Get collection
        collection = chroma_features.get_collection(name=collection_name)
        assert collection is not None
        assert collection.name == collection_name

    def test_get_collection_not_found(self, chroma_features):
        """Test getting non-existent collection."""
        with pytest.raises(ValueError):
            chroma_features.get_collection(name="non_existent")

    def test_delete_collection_success(self, chroma_features):
        """Test successful collection deletion."""
        collection_name = "delete_test_collection"
        
        # Create collection first
        chroma_features.create_collection(name=collection_name)
        
        # Delete collection
        result = chroma_features.delete_collection(name=collection_name)
        assert result is True

    def test_delete_collection_not_found(self, chroma_features):
        """Test deleting non-existent collection."""
        result = chroma_features.delete_collection(name="non_existent")
        assert result is False

    def test_list_collections(self, chroma_features):
        """Test listing collections."""
        # Create some collections
        chroma_features.create_collection(name="collection1")
        chroma_features.create_collection(name="collection2")
        
        collections = chroma_features.list_collections()
        collection_names = [col.name for col in collections]
        
        assert "collection1" in collection_names
        assert "collection2" in collection_names

    def test_add_documents_to_collection(self, chroma_features, sample_collection_data):
        """Test adding documents to collection."""
        collection_name = "add_docs_test"
        collection = chroma_features.create_collection(name=collection_name)
        
        result = chroma_features.add_documents_to_collection(
            collection_name=collection_name,
            documents=sample_collection_data['documents'],
            metadatas=sample_collection_data['metadatas'],
            ids=sample_collection_data['ids']
        )
        
        assert result is True

    def test_query_collection(self, chroma_features, sample_collection_data):
        """Test querying collection."""
        collection_name = "query_test"
        collection = chroma_features.create_collection(name=collection_name)
        
        # Add documents first
        chroma_features.add_documents_to_collection(
            collection_name=collection_name,
            documents=sample_collection_data['documents'],
            metadatas=sample_collection_data['metadatas'],
            ids=sample_collection_data['ids']
        )
        
        # Query collection
        results = chroma_features.query_collection(
            collection_name=collection_name,
            query_texts=["machine learning"],
            n_results=3
        )
        
        assert 'ids' in results
        assert 'documents' in results
        assert 'metadatas' in results
        assert len(results['ids'][0]) <= 3

    def test_get_collection_stats(self, chroma_features, sample_collection_data):
        """Test getting collection statistics."""
        collection_name = "stats_test"
        collection = chroma_features.create_collection(name=collection_name)
        
        # Add documents first
        chroma_features.add_documents_to_collection(
            collection_name=collection_name,
            documents=sample_collection_data['documents'],
            metadatas=sample_collection_data['metadatas'],
            ids=sample_collection_data['ids']
        )
        
        stats = chroma_features.get_collection_stats(collection_name)
        
        assert 'count' in stats
        assert 'name' in stats
        assert stats['count'] == len(sample_collection_data['documents'])
        assert stats['name'] == collection_name

    def test_update_collection_metadata(self, chroma_features):
        """Test updating collection metadata."""
        collection_name = "metadata_test"
        collection = chroma_features.create_collection(
            name=collection_name,
            metadata={"version": "1.0"}
        )
        
        # Update metadata
        new_metadata = {"version": "2.0", "description": "Updated collection"}
        result = chroma_features.update_collection_metadata(
            collection_name=collection_name,
            metadata=new_metadata
        )
        
        assert result is True

    def test_backup_collection(self, chroma_features, sample_collection_data, temp_dir):
        """Test backing up collection."""
        collection_name = "backup_test"
        collection = chroma_features.create_collection(name=collection_name)
        
        # Add documents first
        chroma_features.add_documents_to_collection(
            collection_name=collection_name,
            documents=sample_collection_data['documents'],
            metadatas=sample_collection_data['metadatas'],
            ids=sample_collection_data['ids']
        )
        
        backup_path = Path(temp_dir) / "backup.json"
        result = chroma_features.backup_collection(
            collection_name=collection_name,
            backup_path=str(backup_path)
        )
        
        assert result is True
        assert backup_path.exists()

    def test_restore_collection(self, chroma_features, sample_collection_data, temp_dir):
        """Test restoring collection from backup."""
        collection_name = "restore_test"
        backup_collection_name = "backup_for_restore"
        
        # Create and backup a collection
        collection = chroma_features.create_collection(name=backup_collection_name)
        chroma_features.add_documents_to_collection(
            collection_name=backup_collection_name,
            documents=sample_collection_data['documents'],
            metadatas=sample_collection_data['metadatas'],
            ids=sample_collection_data['ids']
        )
        
        backup_path = Path(temp_dir) / "restore_backup.json"
        chroma_features.backup_collection(
            collection_name=backup_collection_name,
            backup_path=str(backup_path)
        )
        
        # Restore to new collection
        result = chroma_features.restore_collection(
            collection_name=collection_name,
            backup_path=str(backup_path)
        )
        
        assert result is True
        
        # Verify restored collection
        stats = chroma_features.get_collection_stats(collection_name)
        assert stats['count'] == len(sample_collection_data['documents'])

    def test_optimize_collection(self, chroma_features, sample_collection_data):
        """Test collection optimization."""
        collection_name = "optimize_test"
        collection = chroma_features.create_collection(name=collection_name)
        
        # Add documents first
        chroma_features.add_documents_to_collection(
            collection_name=collection_name,
            documents=sample_collection_data['documents'],
            metadatas=sample_collection_data['metadatas'],
            ids=sample_collection_data['ids']
        )
        
        # Optimize collection
        result = chroma_features.optimize_collection(collection_name)
        
        # Note: ChromaDB might not have explicit optimization,
        # so we just check that the method doesn't fail
        assert result is not None

    def test_get_similar_documents(self, chroma_features, sample_collection_data):
        """Test finding similar documents."""
        collection_name = "similarity_test"
        collection = chroma_features.create_collection(name=collection_name)
        
        # Add documents first
        chroma_features.add_documents_to_collection(
            collection_name=collection_name,
            documents=sample_collection_data['documents'],
            metadatas=sample_collection_data['metadatas'],
            ids=sample_collection_data['ids']
        )
        
        # Find similar documents
        similar_docs = chroma_features.get_similar_documents(
            collection_name=collection_name,
            document_id="doc1",
            n_results=3
        )
        
        assert 'ids' in similar_docs
        assert 'documents' in similar_docs
        assert len(similar_docs['ids'][0]) <= 3

    def test_batch_operations(self, chroma_features):
        """Test batch operations on collections."""
        collection_name = "batch_test"
        collection = chroma_features.create_collection(name=collection_name)
        
        # Create batch data
        batch_size = 50
        documents = [f"Batch document {i}" for i in range(batch_size)]
        metadatas = [{"batch": "test", "index": i} for i in range(batch_size)]
        ids = [f"batch_doc_{i}" for i in range(batch_size)]
        
        # Add in batch
        result = chroma_features.add_documents_to_collection(
            collection_name=collection_name,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        assert result is True
        
        # Verify batch was added
        stats = chroma_features.get_collection_stats(collection_name)
        assert stats['count'] == batch_size

    def test_error_handling(self, chroma_features):
        """Test error handling in ChromaFeatures."""
        # Test with invalid collection name
        with pytest.raises((ValueError, Exception)):
            chroma_features.get_collection(name="")
        
        # Test querying non-existent collection
        with pytest.raises((ValueError, Exception)):
            chroma_features.query_collection(
                collection_name="non_existent",
                query_texts=["test"]
            )

    def test_collection_exists(self, chroma_features):
        """Test checking if collection exists."""
        collection_name = "exists_test"
        
        # Should not exist initially
        assert not chroma_features.collection_exists(collection_name)
        
        # Create collection
        chroma_features.create_collection(name=collection_name)
        
        # Should exist now
        assert chroma_features.collection_exists(collection_name)

    def test_get_collection_info(self, chroma_features, sample_collection_data):
        """Test getting detailed collection information."""
        collection_name = "info_test"
        collection = chroma_features.create_collection(
            name=collection_name,
            metadata={"description": "Test collection for info"}
        )
        
        # Add some documents
        chroma_features.add_documents_to_collection(
            collection_name=collection_name,
            documents=sample_collection_data['documents'][:3],
            metadatas=sample_collection_data['metadatas'][:3],
            ids=sample_collection_data['ids'][:3]
        )
        
        info = chroma_features.get_collection_info(collection_name)
        
        assert 'name' in info
        assert 'count' in info
        assert 'metadata' in info
        assert info['name'] == collection_name
        assert info['count'] == 3
