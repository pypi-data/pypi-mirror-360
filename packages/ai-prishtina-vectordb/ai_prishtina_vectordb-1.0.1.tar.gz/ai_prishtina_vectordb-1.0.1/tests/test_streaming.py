"""
Unit tests for streaming functionality in AIPrishtina VectorDB.
"""

import unittest
import pytest
import tempfile
import os
from pathlib import Path
import pandas as pd
import numpy as np
from ai_prishtina_vectordb.data_sources import DataSource
from ai_prishtina_vectordb.logger import AIPrishtinaLogger

class TestStreaming(unittest.TestCase):
    """Test cases for streaming functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = AIPrishtinaLogger(level="DEBUG")
        self.temp_dir = Path("temp_test_dir")
        self.temp_dir.mkdir(exist_ok=True)
        
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
        
    @pytest.mark.asyncio
    async def test_stream_from_file(self):
        """Test streaming from a file."""
        # Create test file
        file_path = Path(self.temp_dir) / "test.txt"
        with open(file_path, "w") as f:
            f.write("Line 1\nLine 2\nLine 3")
            
        source = DataSource(source_type="text")
        batches = []
        async for batch in source.stream_data(file_path, batch_size=2):
            batches.append(batch)
        
        self.assertEqual(len(batches), 2)
        self.assertEqual(len(batches[0]), 2)
        self.assertEqual(len(batches[1]), 1)
        
    @pytest.mark.asyncio
    async def test_stream_from_dataframe(self):
        """Test streaming from a DataFrame."""
        df = pd.DataFrame({
            "text": ["A", "B", "C", "D", "E"],
            "metadata": [1, 2, 3, 4, 5]
        })
        
        source = DataSource(source_type="text")
        batches = []
        async for batch in source.stream_data(df, text_column="text", batch_size=2):
            batches.append(batch)
        
        self.assertEqual(len(batches), 3)
        self.assertEqual(len(batches[0]), 2)
        self.assertEqual(len(batches[1]), 2)
        self.assertEqual(len(batches[2]), 1)
        
    @pytest.mark.asyncio
    async def test_stream_from_list(self):
        """Test streaming from a list of dictionaries."""
        data = [
            {"text": "A", "meta": 1},
            {"text": "B", "meta": 2},
            {"text": "C", "meta": 3}
        ]
        
        source = DataSource(source_type="text")
        batches = []
        async for batch in source.stream_data(data, text_column="text", batch_size=2):
            batches.append(batch)
        
        self.assertEqual(len(batches), 2)
        self.assertEqual(len(batches[0]), 2)
        self.assertEqual(len(batches[1]), 1)
        
    @pytest.mark.asyncio
    async def test_stream_from_binary(self):
        """Test streaming from binary data."""
        data = np.array([[1, 2], [3, 4], [5, 6]])
        
        source = DataSource(source_type="binary")
        batches = []
        async for batch in source.stream_data(data, batch_size=2):
            batches.append(batch)
        
        self.assertEqual(len(batches), 2)
        self.assertEqual(len(batches[0]), 2)
        self.assertEqual(len(batches[1]), 1)

if __name__ == '__main__':
    unittest.main() 