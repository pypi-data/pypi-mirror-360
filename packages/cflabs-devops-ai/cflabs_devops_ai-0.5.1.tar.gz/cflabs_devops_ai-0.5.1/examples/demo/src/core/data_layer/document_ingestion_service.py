from typing import List, Dict, Any, Optional
from pathlib import Path
from src.base_classes.data_layer_class import DataSource, DocumentProcessor
from src.config import Config
from src.core.data_layer.sources.local_source import LocalDataSource
from src.core.data_layer.sources.s3_source import S3DataSource
from src.core.data_layer.processors.pdf_processor import PDFProcessor
from src.core.data_layer.processors.text_processor import TextProcessor
from src.core.data_layer.processors.docx_processor import DocxProcessor  
from src.core.data_layer.processors.pptx_processor import PptxProcessor
from src.utils.logger import get_logger, time_function, log_function_call

logger = get_logger(__name__)

class DocumentIngestionService:
    """Service for ingesting single documents from various sources and formats"""
    
    def __init__(self):
        self.processors: List[DocumentProcessor] = [
            PDFProcessor(),
            TextProcessor(),
            DocxProcessor(),
            PptxProcessor()
        ]
        
        # Supported file extensions
        self.supported_extensions = set()
        for processor in self.processors:
            self.supported_extensions.update(processor.get_supported_extensions())
        
        logger.info(f"Initialized DocumentIngestionService with supported extensions: {self.supported_extensions}")
    
    def create_data_source(self, source_type: str, **kwargs) -> DataSource:
        """Create a data source based on type"""
        if source_type.lower() == 'local':
            base_path = kwargs.get('base_path')
            return LocalDataSource(base_path)
        elif source_type.lower() == 's3':
            bucket_name = kwargs.get('bucket_name')
            if not bucket_name:
                raise ValueError("bucket_name is required for S3 data source")
            
            return S3DataSource(bucket_name=bucket_name)
        else:
            raise ValueError(f"Unsupported data source type: {source_type}")
    
    def get_processor_for_file(self, file_extension: str) -> Optional[DocumentProcessor]:
        """Get the appropriate processor for a file extension"""
        for processor in self.processors:
            if processor.can_process(file_extension):
                return processor
        return None
    
    def is_supported_file(self, filename: str) -> bool:
        """Check if a file is supported"""
        file_extension = Path(filename).suffix.lower()
        return file_extension in self.supported_extensions
    
    @time_function
    @log_function_call
    def process_file(self, data_source: DataSource, file_path: str) -> List[Dict[str, Any]]:
        """Process a single file from the data source"""
        logger.info(f"Processing file: {file_path}")
        
        if not self.is_supported_file(file_path):
            raise ValueError(f"Unsupported file type: {file_path}")
        
        if not data_source.file_exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_extension = Path(file_path).suffix.lower()
        processor = self.get_processor_for_file(file_extension)
        
        if not processor:
            raise ValueError(f"No processor found for file type: {file_extension}")
        
        with data_source.get_file(file_path) as file:
            return processor.process(file, Path(file_path).name) 