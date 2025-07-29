"""Tests for the AIPrishtinaLogger class."""

import os
import pytest
import asyncio
from pathlib import Path
from ai_prishtina_vectordb.logger import AIPrishtinaLogger

@pytest.fixture
def temp_log_file(tmp_path):
    """Create a temporary log file for testing."""
    return tmp_path / "test.log"

@pytest.fixture
def logger(temp_log_file):
    """Create a logger instance for testing."""
    return AIPrishtinaLogger(
        name="test_logger",
        level="DEBUG",
        log_file=temp_log_file
    )

def test_logger_initialization(logger):
    """Test logger initialization."""
    assert logger.name == "test_logger"
    assert logger.level == 10  # DEBUG level
    assert logger.log_file is not None

def test_logger_without_file():
    """Test logger initialization without log file."""
    logger = AIPrishtinaLogger(name="test_logger", level="INFO")
    assert logger.log_file is None

@pytest.mark.asyncio
async def test_async_debug(logger, temp_log_file):
    """Test async debug logging."""
    test_message = "Test debug message"
    await logger.debug(test_message)
    
    # Wait a bit for the async operation to complete
    await asyncio.sleep(0.1)
    
    assert temp_log_file.exists()
    with open(temp_log_file, 'r') as f:
        log_content = f.read()
        assert test_message in log_content
        assert "DEBUG" in log_content

@pytest.mark.asyncio
async def test_async_info(logger, temp_log_file):
    """Test async info logging."""
    test_message = "Test info message"
    await logger.info(test_message)
    
    await asyncio.sleep(0.1)
    
    assert temp_log_file.exists()
    with open(temp_log_file, 'r') as f:
        log_content = f.read()
        assert test_message in log_content
        assert "INFO" in log_content

@pytest.mark.asyncio
async def test_async_warning(logger, temp_log_file):
    """Test async warning logging."""
    test_message = "Test warning message"
    await logger.warning(test_message)
    
    await asyncio.sleep(0.1)
    
    assert temp_log_file.exists()
    with open(temp_log_file, 'r') as f:
        log_content = f.read()
        assert test_message in log_content
        assert "WARNING" in log_content

@pytest.mark.asyncio
async def test_async_error(logger, temp_log_file):
    """Test async error logging."""
    test_message = "Test error message"
    await logger.error(test_message)
    
    await asyncio.sleep(0.1)
    
    assert temp_log_file.exists()
    with open(temp_log_file, 'r') as f:
        log_content = f.read()
        assert test_message in log_content
        assert "ERROR" in log_content

@pytest.mark.asyncio
async def test_async_critical(logger, temp_log_file):
    """Test async critical logging."""
    test_message = "Test critical message"
    await logger.critical(test_message)
    
    await asyncio.sleep(0.1)
    
    assert temp_log_file.exists()
    with open(temp_log_file, 'r') as f:
        log_content = f.read()
        assert test_message in log_content
        assert "CRITICAL" in log_content

@pytest.mark.asyncio
async def test_concurrent_logging(logger, temp_log_file):
    """Test concurrent logging operations."""
    messages = [
        "Debug message",
        "Info message",
        "Warning message",
        "Error message",
        "Critical message"
    ]
    
    # Create multiple logging tasks
    tasks = [
        logger.debug(messages[0]),
        logger.info(messages[1]),
        logger.warning(messages[2]),
        logger.error(messages[3]),
        logger.critical(messages[4])
    ]
    
    # Execute all tasks concurrently
    await asyncio.gather(*tasks)
    
    # Wait for all operations to complete
    await asyncio.sleep(0.1)
    
    assert temp_log_file.exists()
    with open(temp_log_file, 'r') as f:
        log_content = f.read()
        for message in messages:
            assert message in log_content

def test_logger_cleanup():
    """Test logger cleanup on deletion."""
    logger = AIPrishtinaLogger()
    # The __del__ method should be called when the logger is deleted
    del logger 