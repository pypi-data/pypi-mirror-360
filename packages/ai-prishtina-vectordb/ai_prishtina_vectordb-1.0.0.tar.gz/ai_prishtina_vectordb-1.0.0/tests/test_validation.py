"""
Unit tests for validation functionality in AIPrishtina VectorDB.
"""

import unittest
from ai_prishtina_vectordb.validation import (
    validate_documents,
    validate_metadata,
    validate_ids,
    ValidationError
)

class TestValidation(unittest.TestCase):
    """Test cases for validation functionality."""
    
    def test_validate_documents(self):
        """Test document validation."""
        # Test valid documents
        valid_docs = ["Welcome to AIPrishtina", "Test document"]
        self.assertTrue(validate_documents(valid_docs))
        
        # Test invalid documents
        invalid_docs = [None, "", "   "]
        with self.assertRaises(ValidationError):
            validate_documents(invalid_docs)
            
    def test_validate_metadata(self):
        """Test metadata validation."""
        # Test valid metadata
        valid_metadata = [
            {"source": "web", "type": "text"},
            {"source": "file", "type": "pdf"}
        ]
        self.assertTrue(validate_metadata(valid_metadata))
        
        # Test invalid metadata
        invalid_metadata = [None, {}, {"": "value"}]
        with self.assertRaises(ValidationError):
            validate_metadata(invalid_metadata)
            
    def test_validate_ids(self):
        """Test ID validation."""
        # Test valid IDs
        valid_ids = ["doc1", "doc2", "doc3"]
        self.assertTrue(validate_ids(valid_ids))
        
        # Test invalid IDs
        invalid_ids = [None, "", "   "]
        with self.assertRaises(ValidationError):
            validate_ids(invalid_ids)
            
    def test_validate_lengths(self):
        """Test length validation across documents, metadata, and IDs."""
        # Test matching lengths
        docs = ["doc1", "doc2"]
        metadata = [{"source": "web"}, {"source": "file"}]
        ids = ["id1", "id2"]
        self.assertTrue(validate_documents(docs, metadata, ids))
        
        # Test mismatched lengths
        docs = ["doc1", "doc2"]
        metadata = [{"source": "web"}]
        ids = ["id1", "id2"]
        with self.assertRaises(ValidationError):
            validate_documents(docs, metadata, ids)

if __name__ == '__main__':
    unittest.main() 