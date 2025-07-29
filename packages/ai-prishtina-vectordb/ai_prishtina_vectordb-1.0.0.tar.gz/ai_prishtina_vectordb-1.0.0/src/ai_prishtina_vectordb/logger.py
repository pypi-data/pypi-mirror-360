"""
Logging functionality for AIPrishtina VectorDB.
"""

import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any
import aiofiles
import asyncio
from pathlib import Path

class AIPrishtinaLogger:
    """Asynchronous logger for AIPrishtina VectorDB."""

    def __init__(self, name: str = "ai_prishtina_vectordb", level: str = "INFO", log_file: Optional[str] = None, log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"):
        """Initialize the logger.
        
        Args:
            name: Name of the logger
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Optional path to log file
            log_format: Format string for log messages
        """
        self.name = name
        self.level = getattr(logging, level.upper())
        self.log_file = log_file
        self.log_format = log_format
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.level)
        
        # Create formatter
        formatter = logging.Formatter(log_format)
        
        # Add console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # Add file handler if log_file is specified
        if log_file:
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        
    async def _write_to_file(self, message: str) -> None:
        """Write log message to file asynchronously.
        
        Args:
            message: Log message to write
        """
        if self.log_file:
            try:
                async with aiofiles.open(self.log_file, 'a') as f:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    await f.write(f"{timestamp} - {message}\n")
            except Exception as e:
                self.logger.error(f"Failed to write to log file: {str(e)}")
                
    async def debug(self, message: str, **kwargs) -> None:
        """Log debug message.
        
        Args:
            message: Debug message
            **kwargs: Additional context
        """
        self.logger.debug(message, **kwargs)
        await self._write_to_file(f"DEBUG - {message}")
        
    async def info(self, message: str, **kwargs) -> None:
        """Log info message.
        
        Args:
            message: Info message
            **kwargs: Additional context
        """
        self.logger.info(message, **kwargs)
        await self._write_to_file(f"INFO - {message}")
        
    async def warning(self, message: str, **kwargs) -> None:
        """Log warning message.
        
        Args:
            message: Warning message
            **kwargs: Additional context
        """
        self.logger.warning(message, **kwargs)
        await self._write_to_file(f"WARNING - {message}")
        
    async def error(self, message: str, **kwargs) -> None:
        """Log error message.
        
        Args:
            message: Error message
            **kwargs: Additional context
        """
        self.logger.error(message, **kwargs)
        await self._write_to_file(f"ERROR - {message}")
        
    async def critical(self, message: str, **kwargs) -> None:
        """Log critical message.
        
        Args:
            message: Critical message
            **kwargs: Additional context
        """
        self.logger.critical(message, **kwargs)
        await self._write_to_file(f"CRITICAL - {message}")
        
    async def log_metrics(self, metrics: Dict[str, Any]) -> None:
        """Log metrics data.
        
        Args:
            metrics: Dictionary of metrics to log
        """
        message = f"Metrics: {metrics}"
        self.logger.info(message)
        await self._write_to_file(f"METRICS - {message}")
        
    async def log_performance(self, operation: str, duration: float) -> None:
        """Log performance data.
        
        Args:
            operation: Operation name
            duration: Operation duration in seconds
        """
        message = f"Performance - {operation}: {duration:.2f}s"
        self.logger.info(message)
        await self._write_to_file(f"PERFORMANCE - {message}")
        
    async def set_level(self, level: int) -> None:
        """Set logging level.
        
        Args:
            level: New logging level
        """
        self.level = level
        self.logger.setLevel(level)
        for handler in self.logger.handlers:
            handler.setLevel(level)
            
    async def close(self) -> None:
        """Close all handlers."""
        for handler in self.logger.handlers:
            handler.close()
            self.logger.removeHandler(handler)

# Create default logger instance
logger = AIPrishtinaLogger() 