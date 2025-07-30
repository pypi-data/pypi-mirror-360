from abc import ABC, abstractmethod
from typing import List, Dict, Any, BinaryIO

class DataSource(ABC):
    """Abstract base class for data sources"""
    
    @abstractmethod
    def get_file(self, file_path: str) -> BinaryIO:
        """Retrieve a file from the data source"""
        pass
    
    @abstractmethod
    def file_exists(self, file_path: str) -> bool:
        """Check if a file exists in the data source"""
        pass

class DocumentProcessor(ABC):
    """Abstract base class for document processors"""
    
    @abstractmethod
    def can_process(self, file_extension: str) -> bool:
        """Check if this processor can handle the given file type"""
        pass
    
    @abstractmethod
    def process(self, file: BinaryIO, filename: str) -> List[Dict[str, Any]]:
        """Process the file and return structured document data"""
        pass
    
    @abstractmethod
    def get_supported_extensions(self) -> List[str]:
        """Return list of supported file extensions"""
        pass 