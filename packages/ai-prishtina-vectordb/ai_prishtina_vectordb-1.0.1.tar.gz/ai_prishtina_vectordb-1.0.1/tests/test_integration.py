"""Integration tests for AI Prishtina VectorDB."""

import pytest
import asyncio
import tempfile
import shutil
import os
from pathlib import Path
import pandas as pd
import numpy as np
from ai_prishtina_vectordb import Database, DataSource, EmbeddingModel
from ai_prishtina_vectordb.features import FeatureExtractor, FeatureConfig
from ai_prishtina_vectordb.logger import AIPrishtinaLogger
from ai_prishtina_vectordb.metrics import MetricsCollector


@pytest.fixture(scope="function")
def temp_dir():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def sample_data():
    """Create sample data for testing."""
    return {
        'documents': [
            "This is a sample document about machine learning.",
            "Vector databases are useful for similarity search.",
            "ChromaDB is a powerful vector database solution.",
            "AI and machine learning are transforming industries.",
            "Natural language processing enables text understanding."
        ],
        'metadatas': [
            {"category": "ml", "source": "test"},
            {"category": "database", "source": "test"},
            {"category": "database", "source": "test"},
            {"category": "ml", "source": "test"},
            {"category": "nlp", "source": "test"}
        ],
        'ids': ["doc1", "doc2", "doc3", "doc4", "doc5"]
    }


@pytest.fixture(scope="function")
def sample_csv_file(temp_dir):
    """Create a sample CSV file for testing."""
    data = pd.DataFrame({
        'text': [
            "Sample text about AI",
            "Machine learning algorithms",
            "Deep learning networks",
            "Natural language processing"
        ],
        'category': ['ai', 'ml', 'dl', 'nlp'],
        'score': [0.9, 0.8, 0.95, 0.85]
    })
    
    csv_path = Path(temp_dir) / "sample_data.csv"
    data.to_csv(csv_path, index=False)
    return str(csv_path)


class TestDatabaseIntegration:
    """Integration tests for Database functionality."""

    @pytest.mark.asyncio
    async def test_database_basic_operations(self, temp_dir, sample_data):
        """Test basic database operations."""
        # Initialize database
        db = Database(
            collection_name="test_collection",
            config={"persist_directory": temp_dir}
        )
        
        # Add documents
        await db.add(
            documents=sample_data['documents'],
            metadatas=sample_data['metadatas'],
            ids=sample_data['ids']
        )
        
        # Query documents
        results = await db.query(
            query_texts=["machine learning"],
            n_results=3
        )
        
        assert len(results['ids'][0]) == 3
        assert len(results['documents'][0]) == 3
        assert len(results['metadatas'][0]) == 3
        
        # Get specific documents
        get_results = await db.get(ids=["doc1", "doc3"])
        assert len(get_results['ids']) == 2
        assert "doc1" in get_results['ids']
        assert "doc3" in get_results['ids']

    @pytest.mark.asyncio
    async def test_database_with_custom_embeddings(self, temp_dir, sample_data):
        """Test database with custom embedding model."""
        # Initialize embedding model
        embedding_model = EmbeddingModel(model_name="all-MiniLM-L6-v2")
        
        # Generate embeddings
        embeddings = await embedding_model.encode(sample_data['documents'])
        
        # Initialize database
        db = Database(
            collection_name="test_embeddings",
            config={"persist_directory": temp_dir}
        )
        
        # Add with custom embeddings
        await db.add(
            embeddings=embeddings,
            documents=sample_data['documents'],
            metadatas=sample_data['metadatas'],
            ids=sample_data['ids']
        )
        
        # Query
        results = await db.query(
            query_texts=["vector database"],
            n_results=2
        )
        
        assert len(results['ids'][0]) == 2


class TestDataSourceIntegration:
    """Integration tests for DataSource functionality."""

    @pytest.mark.asyncio
    async def test_load_from_csv(self, sample_csv_file):
        """Test loading data from CSV file."""
        data_source = DataSource()
        
        data = await data_source.load_data(
            source=sample_csv_file,
            text_column="text",
            metadata_columns=["category", "score"]
        )
        
        assert len(data['documents']) == 4
        assert len(data['metadatas']) == 4
        assert len(data['ids']) == 4
        assert data['metadatas'][0]['category'] == 'ai'

    @pytest.mark.asyncio
    async def test_stream_from_csv(self, sample_csv_file):
        """Test streaming data from CSV file."""
        data_source = DataSource()
        
        batches = []
        async for batch in data_source.stream_data(
            source=sample_csv_file,
            batch_size=2,
            text_column="text",
            metadata_columns=["category"]
        ):
            batches.append(batch)
        
        assert len(batches) == 2  # 4 items with batch_size=2
        assert len(batches[0]['documents']) == 2
        assert len(batches[1]['documents']) == 2

    @pytest.mark.asyncio
    async def test_load_from_dataframe(self):
        """Test loading data from pandas DataFrame."""
        df = pd.DataFrame({
            'content': ['Text 1', 'Text 2', 'Text 3'],
            'type': ['A', 'B', 'A'],
            'value': [1, 2, 3]
        })
        
        data_source = DataSource()
        data = await data_source.load_data(
            source=df,
            text_column="content",
            metadata_columns=["type", "value"]
        )
        
        assert len(data['documents']) == 3
        assert data['documents'][0] == 'Text 1'
        assert data['metadatas'][0]['type'] == 'A'


class TestFeatureIntegration:
    """Integration tests for Feature extraction."""

    @pytest.mark.asyncio
    async def test_feature_extraction_workflow(self, temp_dir):
        """Test complete feature extraction workflow."""
        # Configure feature extraction
        config = FeatureConfig(
            collection_name="feature_test",
            persist_directory=temp_dir,
            embedding_function="all-MiniLM-L6-v2"
        )
        
        # Initialize feature extractor
        extractor = FeatureExtractor(config)
        
        # Extract features from text
        text = "This is a test document for feature extraction."
        features = await extractor.extract_text_features(text)
        
        assert isinstance(features, np.ndarray)
        assert features.shape[0] > 0  # Should have some dimensions


class TestEndToEndWorkflow:
    """End-to-end integration tests."""

    @pytest.mark.asyncio
    async def test_complete_workflow(self, temp_dir, sample_csv_file):
        """Test complete workflow from data loading to querying."""
        # Initialize components
        data_source = DataSource()
        db = Database(
            collection_name="e2e_test",
            config={"persist_directory": temp_dir}
        )
        logger = AIPrishtinaLogger(name="e2e_test")
        metrics = MetricsCollector()
        
        # Load data
        await logger.info("Loading data from CSV")
        data = await data_source.load_data(
            source=sample_csv_file,
            text_column="text",
            metadata_columns=["category", "score"]
        )
        
        # Add to database
        await logger.info("Adding data to database")
        start_time = metrics.start_timer("add_operation")
        await db.add(
            documents=data['documents'],
            metadatas=data['metadatas'],
            ids=data['ids']
        )
        metrics.end_timer("add_operation", start_time)
        
        # Query database
        await logger.info("Querying database")
        start_time = metrics.start_timer("query_operation")
        results = await db.query(
            query_texts=["machine learning"],
            n_results=2
        )
        metrics.end_timer("query_operation", start_time)
        
        # Verify results
        assert len(results['ids'][0]) == 2
        assert len(results['documents'][0]) == 2
        
        # Check metrics
        add_time = metrics.get_metric("add_operation")
        query_time = metrics.get_metric("query_operation")
        
        assert add_time is not None
        assert query_time is not None
        assert add_time > 0
        assert query_time > 0
        
        await logger.info(f"Add operation took: {add_time:.4f}s")
        await logger.info(f"Query operation took: {query_time:.4f}s")

    @pytest.mark.asyncio
    async def test_batch_processing_workflow(self, temp_dir):
        """Test batch processing workflow."""
        # Create larger dataset
        documents = [f"Document {i} about topic {i % 3}" for i in range(100)]
        metadatas = [{"topic": i % 3, "index": i} for i in range(100)]
        ids = [f"doc_{i}" for i in range(100)]
        
        # Initialize database
        db = Database(
            collection_name="batch_test",
            config={"persist_directory": temp_dir}
        )
        
        # Add in batches
        batch_size = 20
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i + batch_size]
            batch_meta = metadatas[i:i + batch_size]
            batch_ids = ids[i:i + batch_size]
            
            await db.add(
                documents=batch_docs,
                metadatas=batch_meta,
                ids=batch_ids
            )
        
        # Query and verify
        results = await db.query(
            query_texts=["topic 1"],
            n_results=10
        )
        
        assert len(results['ids'][0]) == 10
        
        # Test filtering
        filtered_results = await db.query(
            query_texts=["document"],
            n_results=5,
            where={"topic": 1}
        )
        
        assert len(filtered_results['ids'][0]) <= 5
        # Verify all results have topic=1
        for metadata in filtered_results['metadatas'][0]:
            assert metadata['topic'] == 1


@pytest.mark.skipif(
    os.getenv("SKIP_SLOW_TESTS") == "true",
    reason="Slow integration tests skipped"
)
class TestPerformanceIntegration:
    """Performance integration tests."""

    @pytest.mark.asyncio
    async def test_large_dataset_performance(self, temp_dir):
        """Test performance with larger dataset."""
        # Create large dataset
        num_docs = 1000
        documents = [f"Performance test document {i} with content about various topics including AI, ML, and data science." for i in range(num_docs)]
        metadatas = [{"category": f"cat_{i % 10}", "index": i} for i in range(num_docs)]
        ids = [f"perf_doc_{i}" for i in range(num_docs)]
        
        # Initialize components
        db = Database(
            collection_name="performance_test",
            config={"persist_directory": temp_dir}
        )
        metrics = MetricsCollector()
        
        # Measure add performance
        start_time = metrics.start_timer("large_add")
        await db.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        add_time = metrics.end_timer("large_add", start_time)
        
        # Measure query performance
        start_time = metrics.start_timer("large_query")
        results = await db.query(
            query_texts=["AI and machine learning"],
            n_results=50
        )
        query_time = metrics.end_timer("large_query", start_time)
        
        # Performance assertions
        assert add_time < 60.0  # Should complete within 60 seconds
        assert query_time < 5.0  # Query should be fast
        assert len(results['ids'][0]) == 50
        
        print(f"Large dataset performance - Add: {add_time:.2f}s, Query: {query_time:.2f}s")
