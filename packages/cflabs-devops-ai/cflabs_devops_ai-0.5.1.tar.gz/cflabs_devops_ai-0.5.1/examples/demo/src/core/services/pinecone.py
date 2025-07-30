from typing import List, Dict, Any
import os
from threading import Lock
from src.base_classes.vector_class import BaseVectorDB
from src.utils.logger import get_logger, time_function, log_function_call
from pinecone import Pinecone, ServerlessSpec
from src.config import Config
logger = get_logger(__name__)

class PineconeVectorDB(BaseVectorDB):
    """Pinecone vector database implementation."""
    
    def __init__(self, index_name: str = "default", dimension: int = 1024):
        api_key = Config.PINECONE_API_KEY
        if not api_key:
            raise ValueError("PINECONE_API_KEY environment variable is required")
        
        logger.info(f"Initializing PineconeVectorDB with index: {index_name}, dimension: {dimension}")
        
        # Initialize Pinecone client
        self.pc = Pinecone(api_key=api_key)
        
        # Create index if it doesn't exist
        try:
            self.index = self.pc.Index(index_name)
            logger.info(f"Connected to existing index: {index_name}")
        except Exception as e:
            logger.info(f"Index {index_name} not found, creating new index...")
            # Index doesn't exist, create it
            self.pc.create_index(
                name=index_name,
                dimension=dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            self.index = self.pc.Index(index_name)
            logger.info(f"Created new index: {index_name}")
        
        self._lock = Lock()
    
    @time_function
    @log_function_call
    def add_embeddings(self, embeddings: List[List[float]], metadata: List[Dict[str, Any]]) -> None:
        """Add embeddings and metadata to Pinecone."""
        with self._lock:
            if len(embeddings) != len(metadata):
                raise ValueError("Number of embeddings must match number of metadata entries")
            
            # Prepare vectors for Pinecone
            vectors = []
            for i, (embedding, meta) in enumerate(zip(embeddings, metadata)):
                vectors.append({
                    "id": f"doc_{i}",
                    "values": embedding,
                    "metadata": meta
                })
            
            # Upsert in batches
            batch_size = 100
            for i in range(0, len(vectors), batch_size):
                batch = vectors[i:i + batch_size]
                self.index.upsert(vectors=batch)
    
    @time_function
    @log_function_call
    def search(self, query_embedding: List[float], k: int = 20) -> List[Dict[str, Any]]:
        """Search for similar embeddings in Pinecone."""
        with self._lock:
            results = self.index.query(
                vector=query_embedding,
                top_k=k,
                include_metadata=True,
                include_values=True
            )
            
            formatted_results = []
            for i, match in enumerate(results.matches):
                formatted_results.append({
                    "id": match.id,
                    "metadata": match.metadata,
                    "similarity": float(match.score),
                    "values": match.values,  # Include the embedding vectors
                    "index": i
                })
            
            return formatted_results
    
    def save(self, path: str) -> None:
        """Pinecone automatically persists data, so this is a no-op."""
        pass
    
    def load(self, path: str) -> None:
        """Pinecone automatically loads data, so this is a no-op."""
        pass
    
    def clear(self) -> None:
        """Clear all data from the Pinecone index."""
        with self._lock:
            self.index.delete(delete_all=True)