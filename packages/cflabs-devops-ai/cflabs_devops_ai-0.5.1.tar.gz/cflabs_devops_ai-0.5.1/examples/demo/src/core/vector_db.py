from dotenv import load_dotenv
from threading import Lock
from typing import List, Dict, Any
from src.base_classes.vector_class import BaseVectorDB
from src.core.services.pinecone import PineconeVectorDB  
from src.utils.logger import get_logger, time_function, log_function_call


logger = get_logger(__name__)

class VectorDB:
    """Main vector database class that can use different backend implementations."""
    
    def __init__(self, backend: str = "pinecone", **kwargs):
        """
        Initialize vector database with specified backend.
        
        Args:
            backend: pinecone
            **kwargs: Additional arguments for the specific backend
        """
        logger.info(f"Initializing VectorDB with backend: {backend}")
        self.backend_name = backend
        self.backend = self._create_backend(backend, **kwargs)
        self.query_cache: Dict[str, List[float]] = {}
        self._lock = Lock()
    
    @log_function_call
    def _create_backend(self, backend: str, **kwargs) -> BaseVectorDB:
        """Create the appropriate backend implementation."""
        logger.info(f"Creating backend: {backend}")
        if backend == "pinecone":
            return PineconeVectorDB(**kwargs)
        else:
            raise ValueError(f"Unsupported backend: {backend}. Supported backends: pinecone")
    
    @time_function
    @log_function_call
    def add_embeddings(self, embeddings: List[List[float]], metadata: List[Dict[str, Any]]) -> None:
        """Add embeddings and metadata to the vector database."""
        logger.info(f"Adding {len(embeddings)} embeddings to vector database")
        self.backend.add_embeddings(embeddings, metadata)
        logger.info("Embeddings added successfully")
    
    @time_function
    @log_function_call
    def search(self, query_embedding: List[float], k: int = 20) -> List[Dict[str, Any]]:
        """Search for similar embeddings."""
        logger.info(f"Searching vector database with k={k}")
        results = self.backend.search(query_embedding, k)
        logger.info(f"Search completed, found {len(results)} results")
        return results
    
    @time_function
    def save(self, path: str) -> None:
        """Save the vector database."""
        logger.info(f"Saving vector database to: {path}")
        self.backend.save(path)
        logger.info("Vector database saved successfully")
    
    @time_function
    def load(self, path: str) -> None:
        """Load the vector database."""
        logger.info(f"Loading vector database from: {path}")
        self.backend.load(path)
        logger.info("Vector database loaded successfully")
    
    @time_function
    def clear(self) -> None:
        """Clear all data from the vector database."""
        logger.warning("Clearing vector database")
        self.backend.clear()
        with self._lock:
            self.query_cache.clear()
        logger.info("Vector database cleared successfully")


