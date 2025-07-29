"""
ChromaDB-specific features and utilities for AI Prishtina VectorDB.

This module provides advanced features and utilities specifically designed
to enhance ChromaDB functionality and provide a more robust interface.
"""

from typing import Dict, List, Optional, Union, Any
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
from .exceptions import DatabaseError, ValidationError
from .logger import AIPrishtinaLogger
import json
from pathlib import Path

class ChromaFeatures:
    """Advanced features for ChromaDB integration."""

    def __init__(
        self,
        persist_directory: Optional[str] = None,
        settings: Optional[Settings] = None,
        client: Optional[chromadb.Client] = None
    ):
        """
        Initialize ChromaDB features.

        Args:
            persist_directory: Directory to persist the database
            settings: Custom ChromaDB settings
            client: Existing ChromaDB client to use
        """
        self.persist_directory = persist_directory
        self.logger = AIPrishtinaLogger(name="chroma_features")

        if client:
            self.client = client
        else:
            if persist_directory:
                self.client = chromadb.PersistentClient(path=persist_directory)
            else:
                self.client = chromadb.Client()
    
    def create_collection(
        self,
        name: str,
        metadata: Optional[Dict[str, Any]] = None,
        embedding_function: Optional[str] = None
    ) -> chromadb.Collection:
        """
        Create a collection with custom metadata and embedding function.

        Args:
            name: Collection name
            metadata: Collection metadata
            embedding_function: Name of the embedding function to use

        Returns:
            Created collection
        """
        try:
            if embedding_function:
                ef = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=embedding_function
                )
            else:
                ef = None

            return self.client.create_collection(
                name=name,
                metadata=metadata or {},
                embedding_function=ef
            )
        except Exception as e:
            # If collection already exists, get it instead
            try:
                return self.client.get_collection(name)
            except:
                raise DatabaseError(f"Failed to create collection: {str(e)}")

    def get_collection(self, name: str) -> chromadb.Collection:
        """Get an existing collection."""
        try:
            return self.client.get_collection(name)
        except Exception as e:
            raise ValueError(f"Collection '{name}' not found: {str(e)}")

    def delete_collection(self, name: str) -> bool:
        """Delete a collection."""
        try:
            self.client.delete_collection(name)
            return True
        except Exception as e:
            self.logger.logger.error(f"Failed to delete collection '{name}': {str(e)}")
            return False

    def list_collections(self) -> List[chromadb.Collection]:
        """List all collections."""
        try:
            return self.client.list_collections()
        except Exception as e:
            raise DatabaseError(f"Failed to list collections: {str(e)}")

    def collection_exists(self, name: str) -> bool:
        """Check if a collection exists."""
        try:
            self.client.get_collection(name)
            return True
        except:
            return False

    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """
        Get detailed statistics about a collection.

        Args:
            collection_name: Name of the collection

        Returns:
            Dictionary containing collection statistics
        """
        try:
            collection = self.client.get_collection(collection_name)
            count = collection.count()

            return {
                "count": count,
                "name": collection_name,
                "metadata": collection.metadata if hasattr(collection, 'metadata') else {}
            }
        except Exception as e:
            raise DatabaseError(f"Failed to get collection stats: {str(e)}")

    def add_documents_to_collection(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> bool:
        """Add documents to a collection."""
        try:
            collection = self.client.get_collection(collection_name)
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            return True
        except Exception as e:
            self.logger.logger.error(f"Failed to add documents: {str(e)}")
            return False

    def query_collection(
        self,
        collection_name: str,
        query_texts: List[str],
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Query a collection."""
        try:
            collection = self.client.get_collection(collection_name)
            return collection.query(
                query_texts=query_texts,
                n_results=n_results,
                where=where
            )
        except Exception as e:
            raise DatabaseError(f"Failed to query collection: {str(e)}")

    def update_collection_metadata(
        self,
        collection_name: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """Update collection metadata."""
        try:
            collection = self.client.get_collection(collection_name)
            collection.modify(metadata=metadata)
            return True
        except Exception as e:
            self.logger.logger.error(f"Failed to update metadata: {str(e)}")
            return False

    def backup_collection(
        self,
        collection_name: str,
        backup_path: str
    ) -> bool:
        """Backup a collection to a file."""
        try:
            collection = self.client.get_collection(collection_name)
            data = collection.get()

            backup_data = {
                "name": collection_name,
                "metadata": collection.metadata if hasattr(collection, 'metadata') else {},
                "data": data
            }

            with open(backup_path, 'w') as f:
                json.dump(backup_data, f, indent=2)

            return True
        except Exception as e:
            self.logger.logger.error(f"Failed to backup collection: {str(e)}")
            return False

    def restore_collection(
        self,
        collection_name: str,
        backup_path: str
    ) -> bool:
        """Restore a collection from a backup file."""
        try:
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)

            # Create collection
            collection = self.create_collection(
                name=collection_name,
                metadata=backup_data.get("metadata", {})
            )

            # Add data
            data = backup_data["data"]
            if data.get("documents"):
                collection.add(
                    documents=data["documents"],
                    metadatas=data.get("metadatas"),
                    ids=data.get("ids")
                )

            return True
        except Exception as e:
            self.logger.logger.error(f"Failed to restore collection: {str(e)}")
            return False

    def optimize_collection(self, collection_name: str) -> bool:
        """Optimize a collection (placeholder for future optimization features)."""
        try:
            # ChromaDB doesn't have explicit optimization, but we can return success
            # This is a placeholder for future optimization features
            collection = self.client.get_collection(collection_name)
            return True
        except Exception as e:
            self.logger.logger.error(f"Failed to optimize collection: {str(e)}")
            return False

    def get_similar_documents(
        self,
        collection_name: str,
        document_id: str,
        n_results: int = 10
    ) -> Dict[str, Any]:
        """Find documents similar to a given document."""
        try:
            collection = self.client.get_collection(collection_name)

            # Get the document first
            doc_data = collection.get(ids=[document_id])
            if not doc_data["documents"]:
                raise ValueError(f"Document with ID '{document_id}' not found")

            # Query using the document text
            return collection.query(
                query_texts=doc_data["documents"],
                n_results=n_results + 1  # +1 to exclude the original document
            )
        except Exception as e:
            raise DatabaseError(f"Failed to find similar documents: {str(e)}")

    def get_collection_info(self, collection_name: str) -> Dict[str, Any]:
        """Get detailed information about a collection."""
        try:
            collection = self.client.get_collection(collection_name)
            stats = self.get_collection_stats(collection_name)

            return {
                "name": collection_name,
                "count": stats["count"],
                "metadata": stats["metadata"]
            }
        except Exception as e:
            raise DatabaseError(f"Failed to get collection info: {str(e)}")
    
    async def optimize_collection(
        self,
        collection_name: str,
        optimization_params: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Optimize collection for better performance.
        
        Args:
            collection_name: Name of the collection
            optimization_params: Parameters for optimization
        """
        try:
            collection = await self.client.get_collection(collection_name)
            
            # Default optimization parameters
            params = {
                "hnsw_ef_construction": 200,
                "hnsw_m": 16,
                "hnsw_ef_search": 100
            }
            
            if optimization_params:
                params.update(optimization_params)
            
            # Apply optimization
            await collection.update_hnsw_params(
                ef_construction=params["hnsw_ef_construction"],
                m=params["hnsw_m"],
                ef_search=params["hnsw_ef_search"]
            )
        except Exception as e:
            raise DatabaseError(f"Failed to optimize collection: {str(e)}")
    
    async def backup_collection(
        self,
        collection_name: str,
        backup_path: str
    ) -> None:
        """
        Create a backup of a collection.
        
        Args:
            collection_name: Name of the collection
            backup_path: Path to store the backup
        """
        try:
            collection = await self.client.get_collection(collection_name)
            
            # Get all data
            results = await collection.get()
            
            # Save to backup file
            import json
            import os
            
            os.makedirs(backup_path, exist_ok=True)
            backup_file = os.path.join(backup_path, f"{collection_name}_backup.json")
            
            with open(backup_file, 'w') as f:
                json.dump(results, f)
        except Exception as e:
            raise DatabaseError(f"Failed to backup collection: {str(e)}")
    
    async def restore_collection(
        self,
        backup_path: str,
        collection_name: str
    ) -> None:
        """
        Restore a collection from backup.
        
        Args:
            backup_path: Path to the backup file
            collection_name: Name for the restored collection
        """
        try:
            import json
            
            # Load backup data
            with open(backup_path, 'r') as f:
                backup_data = json.load(f)
            
            # Create new collection
            collection = await self.create_collection_with_metadata(
                name=collection_name,
                metadata=backup_data.get('metadatas', [{}])[0]
            )
            
            # Restore data
            await collection.add(
                documents=backup_data['documents'],
                metadatas=backup_data['metadatas'],
                ids=backup_data['ids']
            )
        except Exception as e:
            raise DatabaseError(f"Failed to restore collection: {str(e)}")
    
    async def merge_collections(
        self,
        source_collection: str,
        target_collection: str,
        merge_strategy: str = "append"
    ) -> None:
        """
        Merge two collections.
        
        Args:
            source_collection: Name of the source collection
            target_collection: Name of the target collection
            merge_strategy: Strategy for merging ("append" or "update")
        """
        try:
            source = await self.client.get_collection(source_collection)
            target = await self.client.get_collection(target_collection)
            
            # Get source data
            source_data = await source.get()
            
            if merge_strategy == "append":
                # Simple append
                await target.add(
                    documents=source_data['documents'],
                    metadatas=source_data['metadatas'],
                    ids=source_data['ids']
                )
            elif merge_strategy == "update":
                # Update existing documents
                for doc, meta, doc_id in zip(
                    source_data['documents'],
                    source_data['metadatas'],
                    source_data['ids']
                ):
                    await target.update(
                        ids=[doc_id],
                        documents=[doc],
                        metadatas=[meta]
                    )
            else:
                raise ValidationError(f"Invalid merge strategy: {merge_strategy}")
        except Exception as e:
            raise DatabaseError(f"Failed to merge collections: {str(e)}")
    
    async def get_similarity_matrix(
        self,
        collection_name: str,
        query_ids: List[str],
        n_results: int = 5
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get similarity matrix for a set of documents.
        
        Args:
            collection_name: Name of the collection
            query_ids: List of document IDs to compare
            n_results: Number of similar documents to return
            
        Returns:
            Dictionary containing similarity scores
        """
        try:
            collection = await self.client.get_collection(collection_name)
            results = {}
            
            for query_id in query_ids:
                # Get document
                doc = await collection.get(ids=[query_id])
                if not doc['documents']:
                    continue
                
                # Find similar documents
                similar = await collection.query(
                    query_texts=doc['documents'],
                    n_results=n_results,
                    where={"$ne": {"id": query_id}}
                )
                
                results[query_id] = [
                    {
                        "id": similar['ids'][0][i],
                        "document": similar['documents'][0][i],
                        "similarity": 1 - similar['distances'][0][i]
                    }
                    for i in range(len(similar['ids'][0]))
                ]
            
            return results
        except Exception as e:
            raise DatabaseError(f"Failed to get similarity matrix: {str(e)}") 