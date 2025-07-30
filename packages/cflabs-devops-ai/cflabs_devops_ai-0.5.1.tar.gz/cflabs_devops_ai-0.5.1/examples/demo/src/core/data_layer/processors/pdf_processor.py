import hashlib
from typing import List, Dict, Any, BinaryIO
from src.base_classes.data_layer_class import DocumentProcessor
from src.core.rag_utils import create_documents_from_pdf, chunk_document
from src.utils.logger import get_logger, time_function, log_function_call

logger = get_logger(__name__)

class PDFProcessor(DocumentProcessor):
    """Processor for PDF documents"""
    
    def can_process(self, file_extension: str) -> bool:
        return file_extension.lower() in ['.pdf']
    
    def get_supported_extensions(self) -> List[str]:
        return ['.pdf']
    
    @time_function
    @log_function_call
    def process(self, file: BinaryIO, filename: str) -> List[Dict[str, Any]]:
        """Process PDF file and return structured document data"""
        logger.info(f"Processing PDF file: {filename}")
        
        try:
            # Create documents from PDF (2 pages per document)
            logger.info("Creating documents from PDF")
            documents = create_documents_from_pdf(file, pages_per_doc=2)
            logger.info(f"Created {len(documents)} documents from PDF")
            
            # Process each document to add chunks
            parsed_data = []
            for i, doc in enumerate(documents):
                logger.debug(f"Processing document {i+1}/{len(documents)}")
                
                # Generate original_uuid as hash of content
                content_hash = hashlib.sha256(doc['content'].encode()).hexdigest()
                
                # Update document with proper format
                formatted_doc = {
                    "doc_id": f"{filename}_doc_{i+1}",
                    "original_uuid": content_hash,
                    "content": doc['content'],
                    "source": filename,
                    "file_type": "pdf"
                }
                
                # Add chunks to the document
                chunked_doc = chunk_document(formatted_doc)
                parsed_data.append(chunked_doc)
            
            total_chunks = sum(len(doc['chunks']) for doc in parsed_data)
            logger.info(f"PDF processing completed. Documents: {len(parsed_data)}, Total chunks: {total_chunks}")
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error processing PDF file {filename}: {str(e)}")
            raise 