"""
Document processing example using AIPrishtina VectorDB.

This example demonstrates:
1. Loading and processing different document types (PDF, Word, Excel)
2. Extracting text and metadata from documents
3. Handling different document formats
4. Logging operations
"""

import os
from pathlib import Path
import pandas as pd
from ai_prishtina_vectordb import DataSource, Database
from ai_prishtina_vectordb.logger import AIPrishtinaLogger

# Initialize logger
logger = AIPrishtinaLogger(
    name="document_processing_example",
    level="DEBUG",
    log_file="logs/document_processing.log"
)

def create_sample_documents():
    """Create sample documents for demonstration."""
    logger.info("Creating sample documents")
    
    # Create data directory
    data_dir = Path("data/documents")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Create sample Excel file
    excel_data = {
        "Name": ["John Doe", "Jane Smith", "Bob Johnson"],
        "Age": [30, 25, 35],
        "Department": ["IT", "HR", "Finance"]
    }
    excel_df = pd.DataFrame(excel_data)
    excel_path = data_dir / "sample.xlsx"
    excel_df.to_excel(excel_path, index=False)
    logger.debug(f"Created sample Excel file: {excel_path}")
    
    # Create sample text file (simulating Word document content)
    word_content = """
    Project Report
    
    Title: Machine Learning Implementation
    Author: John Doe
    Date: 2024-03-20
    
    Summary:
    This report discusses the implementation of machine learning models
    in our production environment. We have successfully deployed several
    models that have improved our prediction accuracy by 25%.
    
    Key Findings:
    1. Model performance improved significantly
    2. Processing time reduced by 40%
    3. Resource utilization optimized
    """
    word_path = data_dir / "sample.txt"  # Simulating Word document
    with open(word_path, "w") as f:
        f.write(word_content)
    logger.debug(f"Created sample Word-like file: {word_path}")
    
    # Create sample PDF-like content
    pdf_content = """
    Technical Documentation
    
    System Architecture
    ==================
    
    The system consists of multiple components:
    1. Frontend Service
    2. Backend API
    3. Database Layer
    4. Cache System
    
    Each component is designed for high availability and scalability.
    """
    pdf_path = data_dir / "sample.txt"  # Simulating PDF document
    with open(pdf_path, "w") as f:
        f.write(pdf_content)
    logger.debug(f"Created sample PDF-like file: {pdf_path}")
    
    return data_dir

def load_excel_documents(data_dir: Path):
    """Load and process Excel documents."""
    logger.info("Loading Excel documents")
    
    try:
        source = DataSource(source_type="excel")
        result = source.load_data(
            source=data_dir,
            metadata_columns=["source", "filename"]
        )
        logger.info("Successfully loaded Excel documents")
        return result
    except Exception as e:
        logger.error("Error loading Excel documents", error=str(e))
        return None

def load_word_documents(data_dir: Path):
    """Load and process Word documents."""
    logger.info("Loading Word documents")
    
    try:
        source = DataSource(source_type="word")
        result = source.load_data(
            source=data_dir,
            metadata_columns=["source", "filename"]
        )
        logger.info("Successfully loaded Word documents")
        return result
    except Exception as e:
        logger.error("Error loading Word documents", error=str(e))
        return None

def load_pdf_documents(data_dir: Path):
    """Load and process PDF documents."""
    logger.info("Loading PDF documents")
    
    try:
        source = DataSource(source_type="pdf")
        result = source.load_data(
            source=data_dir,
            metadata_columns=["source", "filename"]
        )
        logger.info("Successfully loaded PDF documents")
        return result
    except Exception as e:
        logger.error("Error loading PDF documents", error=str(e))
        return None

def perform_search(database: Database, query: str, n_results: int = 3):
    """Perform similarity search."""
    logger.info(f"Performing search for query: {query}")
    
    try:
        results = database.query(
            query_texts=[query],
            n_results=n_results
        )
        logger.info(f"Found {len(results['documents'][0])} results")
        return results
    except Exception as e:
        logger.error("Error performing search", error=str(e))
        return None

def main():
    """Main function demonstrating document processing."""
    logger.info("Starting document processing example")
    
    # Create sample documents
    data_dir = create_sample_documents()
    
    # Initialize database
    database = Database()
    
    # Load different document types
    document_results = {}
    
    # Load Excel documents
    excel_result = load_excel_documents(data_dir)
    if excel_result:
        document_results["excel"] = excel_result
    
    # Load Word documents
    word_result = load_word_documents(data_dir)
    if word_result:
        document_results["word"] = word_result
    
    # Load PDF documents
    pdf_result = load_pdf_documents(data_dir)
    if pdf_result:
        document_results["pdf"] = pdf_result
    
    # Add data to database
    for doc_type, result in document_results.items():
        logger.info(f"Adding {doc_type} documents to database")
        try:
            database.add(
                documents=result["documents"],
                metadatas=result["metadatas"],
                ids=result["ids"]
            )
            logger.debug(f"Successfully added {doc_type} documents")
        except Exception as e:
            logger.error(f"Error adding {doc_type} documents", error=str(e))
    
    # Perform searches
    queries = [
        "Find information about machine learning implementation",
        "Search for system architecture details",
        "Look for project reports"
    ]
    
    for query in queries:
        logger.info(f"Processing query: {query}")
        results = perform_search(database, query)
        if results:
            logger.info("Search results:", results=results)

if __name__ == "__main__":
    main() 