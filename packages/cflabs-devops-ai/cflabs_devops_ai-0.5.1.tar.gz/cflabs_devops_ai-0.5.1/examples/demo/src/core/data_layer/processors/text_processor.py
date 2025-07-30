import hashlib
from typing import List, Dict, Any, BinaryIO
from pathlib import Path
from src.base_classes.data_layer_class import DocumentProcessor
from src.core.rag_utils import chunk_document
from src.utils.logger import get_logger, time_function, log_function_call

logger = get_logger(__name__)

class TextProcessor(DocumentProcessor):
    """Processor for text documents (txt, md, etc.)"""
    
    def can_process(self, file_extension: str) -> bool:
        return file_extension.lower() in ['.txt', '.md', '.rst', '.log', '.json', '.xml', '.html', '.htm']
    
    def get_supported_extensions(self) -> List[str]:
        return ['.txt', '.md', '.rst', '.log', '.json', '.xml', '.html', '.htm']
    
    @time_function
    @log_function_call
    def process(self, file: BinaryIO, filename: str) -> List[Dict[str, Any]]:
        """Process text file and return structured document data"""
        logger.info(f"Processing text file: {filename}")
        
        try:
            # Read file content
            content = file.read().decode('utf-8')
            if not content.strip():
                logger.warning(f"Empty text file: {filename}")
                return []
            
            # Generate original_uuid as hash of content
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            
            # Create document
            formatted_doc = {
                "doc_id": f"{filename}_doc_1",
                "original_uuid": content_hash,
                "content": content,
                "source": filename,
                "file_type": Path(filename).suffix.lower()
            }
            
            # Add chunks to the document
            chunked_doc = chunk_document(formatted_doc)
            
            logger.info(f"Text processing completed. Documents: 1, Total chunks: {len(chunked_doc['chunks'])}")
            return [chunked_doc]
            
        except UnicodeDecodeError:
            logger.error(f"Unable to decode text file {filename} as UTF-8")
            raise
        except Exception as e:
            logger.error(f"Error processing text file {filename}: {str(e)}")
            raise 