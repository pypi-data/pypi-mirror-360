"""
Unit tests for data source functionality in AIPrishtina VectorDB.
"""

import unittest
import tempfile
import os
from pathlib import Path
import pandas as pd
import numpy as np
from ai_prishtina_vectordb.data_sources import DataSource
from ai_prishtina_vectordb.logger import AIPrishtinaLogger
import pytest
import shutil

class TestDataSources:
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        yield
        shutil.rmtree(self.temp_dir)

    @pytest.mark.asyncio
    async def test_text_source(self):
        """Test text data source."""
        # Create test file
        file_path = Path(self.temp_dir) / "test.txt"
        with open(file_path, "w") as f:
            f.write("Line 1\nLine 2\nLine 3")
        
        source = DataSource(source_type="text")
        data = await source.load_data(file_path)
        
        assert "documents" in data
        assert len(data["documents"]) == 3
        assert data["documents"][0] == "Line 1"

    @pytest.mark.asyncio
    async def test_image_source(self):
        """Test image data source."""
        # Create dummy image data
        images = np.random.rand(2, 224, 224, 3)
        source = DataSource(source_type="image")
        data = await source.load_data(images)
        
        assert "documents" in data
        assert len(data["documents"]) == 2

    @pytest.mark.asyncio
    async def test_audio_source(self):
        """Test audio data source."""
        # Create dummy audio data
        audio = np.random.rand(2, 16000)
        source = DataSource(source_type="audio")
        data = await source.load_data(audio)
        
        assert "documents" in data
        assert len(data["documents"]) == 2

    @pytest.mark.asyncio
    async def test_video_source(self):
        """Test video data source."""
        # Create dummy video data
        video = np.random.rand(2, 30, 224, 224, 3)
        source = DataSource(source_type="video")
        data = await source.load_data(video)
        
        assert "documents" in data
        assert len(data["documents"]) == 2

    @pytest.mark.asyncio
    async def test_dataframe_source(self):
        """Test DataFrame data source."""
        df = pd.DataFrame({
            "text": ["A", "B", "C"],
            "metadata": [1, 2, 3]
        })
        
        source = DataSource(source_type="text")
        data = await source.load_data(df, text_column="text")
        
        assert "documents" in data
        assert len(data["documents"]) == 3
        assert data["documents"][0] == "A"

if __name__ == '__main__':
    unittest.main() 