import os
from pathlib import Path
from typing import BinaryIO
from src.base_classes.data_layer_class import DataSource
from src.utils.logger import get_logger

logger = get_logger(__name__)

class LocalDataSource(DataSource):
    """Data source for local file system"""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path.cwd()
        logger.info(f"Initialized LocalDataSource with base path: {self.base_path}")
    
    def get_file(self, file_path: str) -> BinaryIO:
        """Retrieve a file from local file system"""
        full_path = self.base_path / file_path
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {full_path}")
        
        logger.debug(f"Opening local file: {full_path}")
        return open(full_path, 'rb')
    
    def file_exists(self, file_path: str) -> bool:
        """Check if a file exists in the local file system"""
        full_path = self.base_path / file_path
        return full_path.exists() 