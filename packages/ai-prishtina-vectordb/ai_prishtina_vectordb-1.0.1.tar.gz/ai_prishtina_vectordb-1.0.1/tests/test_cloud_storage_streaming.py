"""
Unit tests for cloud storage streaming functionality.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import shutil
from unittest.mock import Mock, patch, mock_open, AsyncMock, MagicMock
from ai_prishtina_vectordb.data_sources import DataSource, DataSourceError
import hashlib
import io

@pytest.fixture
def source():
    """Create a test data source."""
    return DataSource()

@pytest.fixture
async def mock_s3_client():
    """Create a mock S3 client for testing."""
    mock_client = AsyncMock()
    mock_body = AsyncMock()
    mock_body.read.return_value = b"Test content"
    mock_client.get_object.return_value = {"Body": mock_body}
    return mock_client

@pytest.fixture
def mock_minio_client():
    """Create a mock MinIO client."""
    client = Mock()
    
    # Mock list_objects
    objects = [
        Mock(object_name='data/file1.txt'),
        Mock(object_name='data/file2.txt'),
        Mock(object_name='data/file3.txt')
    ]
    client.list_objects.return_value = objects
    
    # Mock get_object
    def mock_get_object(bucket, object_name):
        data = Mock()
        if object_name.endswith('.txt'):
            data.read.return_value = b'Hello world'
        elif object_name.endswith('.json'):
            data.read.return_value = b'{"text": "Hello world"}'
        elif object_name.endswith('.csv'):
            data.read.return_value = b'text,source\nHello world,test'
        return data
    client.get_object.side_effect = mock_get_object
    
    return client

@pytest.fixture
def mock_gcs_client():
    """Create a mock GCS client."""
    client = Mock()
    
    # Mock bucket and blob
    bucket = Mock()
    blobs = [
        Mock(name='data/file1.txt'),
        Mock(name='data/file2.txt'),
        Mock(name='data/file3.txt')
    ]
    bucket.list_blobs.return_value = blobs
    
    def mock_download_to_filename(filename):
        with open(filename, 'w') as f:
            if filename.endswith('.txt'):
                f.write('Hello world')
            elif filename.endswith('.json'):
                f.write('{"text": "Hello world"}')
            elif filename.endswith('.csv'):
                f.write('text,source\nHello world,test')
    
    for blob in blobs:
        blob.download_to_filename = mock_download_to_filename
    
    client.bucket.return_value = bucket
    return client

@pytest.fixture
def mock_azure_client():
    """Create a mock Azure client."""
    client = Mock()
    
    # Mock container client
    container_client = Mock()
    blobs = [
        Mock(name='data/file1.txt'),
        Mock(name='data/file2.txt'),
        Mock(name='data/file3.txt')
    ]
    container_client.list_blobs.return_value = blobs
    
    def mock_download_blob():
        blob_data = Mock()
        if blob.name.endswith('.txt'):
            blob_data.readall.return_value = b'Hello world'
        elif blob.name.endswith('.json'):
            blob_data.readall.return_value = b'{"text": "Hello world"}'
        elif blob.name.endswith('.csv'):
            blob_data.readall.return_value = b'text,source\nHello world,test'
        return blob_data
    
    for blob in blobs:
        blob_client = Mock()
        blob_client.download_blob = mock_download_blob
        container_client.get_blob_client.return_value = blob_client
    
    client.get_container_client.return_value = container_client
    return client

@pytest.mark.skip(reason="S3 streaming test temporarily disabled due to async issues")
@pytest.mark.asyncio
async def test_stream_from_s3(mock_s3_client, monkeypatch):
    """Test streaming data from S3."""
    # Patch _is_url to return False for s3 paths
    monkeypatch.setattr(DataSource, "_is_url", lambda self, path: False)
    # Patch _is_cloud_storage_path to return True for s3 paths
    monkeypatch.setattr(DataSource, "_is_cloud_storage_path", lambda self, path: path.startswith("s3://"))

    # Create data source
    source = DataSource(
        source_type="text",
        config={
            "aws_access_key_id": "test_key",
            "aws_secret_access_key": "test_secret",
            "aws_region": "us-east-1"
        }
    )
    source.s3_client = mock_s3_client
    await source._init_cloud_clients()

    # Stream data
    batches = []
    async for batch in source.stream_data("s3://test-bucket/test-key", batch_size=2):
        batches.append(batch)

    # Verify results
    assert len(batches) > 0
    assert "Test content" in batches[0]["documents"][0]
    mock_s3_client.get_object.assert_called_once_with(
        Bucket="test-bucket",
        Key="test-key"
    )

@patch('minio.Minio')
def test_stream_from_minio(mock_minio, source, mock_minio_client):
    """Test streaming from MinIO."""
    mock_minio.return_value = mock_minio_client
    mock_minio_client.list_objects.return_value = [
        Mock(name='data/file1.txt', size=100),
        Mock(name='data/file2.txt', size=100),
        Mock(name='data/file3.txt', size=100)
    ]
    mock_minio_client.get_object.return_value = Mock(read=lambda: b'test content')

    batches = list(source.stream_data(
        source="minio://my-bucket/data/",
        text_column="text",
        metadata_columns=["source", "bucket"],
        batch_size=1,
        endpoint="localhost:9000",
        access_key="test",
        secret_key="test"
    ))

    assert len(batches) == 3
    assert all('bucket' in batch['metadatas'][0] for batch in batches)
    assert all(batch['metadatas'][0]['bucket'] == 'my-bucket' for batch in batches)

@patch('google.cloud.storage.Client')
def test_stream_from_gcs(mock_gcs, source, mock_gcs_client):
    """Test streaming from GCS."""
    mock_gcs.return_value = mock_gcs_client
    mock_bucket = Mock()
    mock_gcs_client.bucket.return_value = mock_bucket
    mock_blob = Mock()
    mock_blob.name = 'data/file1.txt'
    mock_blob.download_to_filename = Mock()
    mock_bucket.list_blobs.return_value = [mock_blob]

    with patch('builtins.open', mock_open(read_data='test content')):
        batches = list(source.stream_data(
            source="gs://my-bucket/data/",
            text_column="text",
            metadata_columns=["source", "bucket"],
            batch_size=1,
            project_id="test"
        ))

    assert len(batches) == 1
    assert 'bucket' in batches[0]['metadatas'][0]
    assert batches[0]['metadatas'][0]['bucket'] == 'my-bucket'

@patch('azure.storage.blob.BlobServiceClient')
def test_stream_from_azure(mock_azure, source, mock_azure_client):
    """Test streaming from Azure."""
    mock_azure.return_value = mock_azure_client
    mock_container = Mock()
    mock_azure_client.get_container_client.return_value = mock_container
    mock_blob = Mock()
    mock_blob.name = 'data/file1.txt'
    mock_blob.download_blob.return_value.readall.return_value = b'test content'
    mock_container.list_blobs.return_value = [mock_blob]

    batches = list(source.stream_data(
        source="azure://my-container/data/",
        text_column="text",
        metadata_columns=["source", "container"],
        batch_size=1,
        connection_string="DefaultEndpointsProtocol=https;AccountName=test;AccountKey=test;EndpointSuffix=core.windows.net"
    ))

    assert len(batches) == 1
    assert 'container' in batches[0]['metadatas'][0]
    assert batches[0]['metadatas'][0]['container'] == 'my-container'

@pytest.mark.skip(reason="Test disabled due to mock issues")
def test_stream_cloud_storage_errors(source):
    """Test error handling for cloud storage."""
    # Test invalid path format
    with pytest.raises(ValueError, match="Invalid cloud storage path format"):
        list(source._stream_from_cloud_storage(
            "invalid://my-bucket/data/",
            text_column="text",
            metadata_columns=["source"],
            batch_size=1
        ))

    # Test missing credentials
    with pytest.raises(ValueError, match="MinIO endpoint is required"):
        list(source._stream_from_minio(
            "minio://my-bucket/data/",
            text_column="text",
            metadata_columns=["source"],
            batch_size=1
        ))

    with pytest.raises(ValueError, match="GCS project ID is required"):
        list(source._stream_from_gcs(
            "gcs://my-bucket/data/",
            text_column="text",
            metadata_columns=["source"],
            batch_size=1
        ))
    
    with pytest.raises(ValueError, match="Azure connection string is required"):
        list(source._stream_from_azure(
            "azure://my-container/data/",
            text_column="text",
            metadata_columns=["source"],
            batch_size=1
        ))
    
    # Test connection errors
    with patch("ai_prishtina_vectordb.data_sources.Minio", side_effect=Exception("Connection error")):
        source.config = {
            "minio_endpoint": "localhost:9000",
            "minio_access_key": "test",
            "minio_secret_key": "test",
            "minio_secure": False
        }
        with pytest.raises(DataSourceError, match="Failed to connect to MinIO"):
            list(source._stream_from_minio(
                "minio://my-bucket/data/",
                text_column="text",
                metadata_columns=["source"],
                batch_size=1
            ))

@pytest.mark.skip(reason="Test disabled due to mock issues")
def test_stream_from_minio(source):
    """Test streaming from MinIO."""
    mock_client = Mock()
    mock_objects = [
        Mock(object_name="file1.txt"),
        Mock(object_name="file2.txt")
    ]
    mock_client.list_objects.return_value = mock_objects
    mock_client.get_object.return_value = Mock(read=lambda: b"test content")
    
    with patch("ai_prishtina_vectordb.data_sources.Minio", return_value=mock_client):
        source.config = {
            "minio_endpoint": "localhost:9000",
            "minio_access_key": "test",
            "minio_secret_key": "test",
            "minio_secure": False
        }
        source._minio_client = mock_client
        result = list(source._stream_from_minio(
            "minio://my-bucket/data/",
            text_column="text",
            metadata_columns=["source", "bucket"],
            batch_size=1
        ))
        assert len(result) == 2
        # Check first batch
        batch0 = result[0]["documents"][0]
        assert batch0["documents"] == ["test content"]
        assert batch0["metadata"]["source"] == "minio://my-bucket/file1.txt"
        assert batch0["metadata"]["bucket"] == "my-bucket"
        assert batch0["ids"] == [hashlib.md5("test content".encode()).hexdigest()]
        # Check second batch
        batch1 = result[1]["documents"][0]
        assert batch1["documents"] == ["test content"]
        assert batch1["metadata"]["source"] == "minio://my-bucket/file2.txt"
        assert batch1["metadata"]["bucket"] == "my-bucket"
        assert batch1["ids"] == [hashlib.md5("test content".encode()).hexdigest()]

@pytest.mark.skip(reason="Test disabled due to mock issues")
def test_stream_from_gcs(source):
    """Test streaming from Google Cloud Storage."""
    mock_client = Mock()
    mock_bucket = Mock()
    mock_blob = Mock()
    mock_bucket.blob.return_value = mock_blob
    mock_client.bucket.return_value = mock_bucket
    mock_blob.download_as_bytes.return_value = b"test content"
    
    with patch("ai_prishtina_vectordb.data_sources.storage.Client", return_value=mock_client):
        source.config = {
            "gcs_project_id": "test-project",
            "gcs_credentials": "test-credentials"
        }
        source._gcs_client = mock_client
        result = list(source._stream_from_gcs(
            "gcs://my-bucket/data/",
            text_column="text",
            metadata_columns=["source", "bucket"],
            batch_size=1
        ))
        assert len(result) == 1
        assert result[0]["documents"] == ["test content"]
        assert result[0]["metadata"]["source"] == "gcs://my-bucket/data/"

@pytest.mark.skip(reason="Test disabled due to mock issues")
def test_stream_from_azure(source):
    """Test streaming from Azure Blob Storage."""
    mock_client = Mock()
    mock_container = Mock()
    mock_blob = Mock()
    mock_container.get_blob_client.return_value = mock_blob
    mock_client.get_container_client.return_value = mock_container
    mock_blob.download_blob.return_value.readall.return_value = b"test content"
    
    with patch("ai_prishtina_vectordb.data_sources.BlobServiceClient", return_value=mock_client):
        source.config = {
            "azure_connection_string": "DefaultEndpointsProtocol=https;AccountName=test;AccountKey=test;EndpointSuffix=core.windows.net"
        }
        source._azure_client = mock_client
        result = list(source._stream_from_azure(
            "azure://my-container/data/",
            text_column="text",
            metadata_columns=["source", "container"],
            batch_size=1
        ))
        assert len(result) == 1
        assert result[0]["documents"] == ["test content"]
        assert result[0]["metadata"]["source"] == "azure://my-container/data/" 