from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseVectorDB(ABC):
    """Abstract base class for vector database implementations."""
    
    @abstractmethod
    def add_embeddings(self, embeddings: List[List[float]], metadata: List[Dict[str, Any]]) -> None:
        """Add embeddings and metadata to the vector database."""
        pass
    
    @abstractmethod
    def search(self, query_embedding: List[float], k: int = 20) -> List[Dict[str, Any]]:
        """Search for similar embeddings and return results with metadata."""
        pass
    
    @abstractmethod
    def save(self, path: str) -> None:
        """Save the vector database to disk."""
        pass
    
    @abstractmethod
    def load(self, path: str) -> None:
        """Load the vector database from disk."""
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """Clear all data from the vector database."""
        pass