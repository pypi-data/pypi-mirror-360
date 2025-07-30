from typing import List, Dict, Any
import hashlib
from src.core.rag_utils import create_documents_from_pdf, chunk_document
from src.utils.logger import get_logger, time_function, log_function_call

logger = get_logger(__name__)

class DataFormatter:
    @time_function
    def __init__(self):
        pass

    @time_function
    @log_function_call
    def parse_pdf_data(self, file) -> List[Dict[str, Any]]:
        """
        Parse PDF file and return data in the exact format:
        List[Dict[str, Any]] where each dict has:
        {
            "doc_id": "doc_1",
            "original_uuid": "hash_string",
            "content": "full document content...",
            "chunks": [
                {
                    "chunk_id": "doc_1_chunk_0",
                    "original_index": 0,
                    "content": "chunk content..."
                },
                {
                    "chunk_id": "doc_1_chunk_1", 
                    "original_index": 1,
                    "content": "chunk content..."
                }
            ]
        }
        """
        logger.info(f"Parsing PDF file: {file.filename}")
        
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
                "doc_id": f"doc_{i+1}",
                "original_uuid": content_hash,
                "content": doc['content']
            }
            
            # Add chunks to the document
            chunked_doc = chunk_document(formatted_doc)
            parsed_data.append(chunked_doc)
        
        total_chunks = sum(len(doc['chunks']) for doc in parsed_data)
        logger.info(f"PDF parsing completed. Documents: {len(parsed_data)}, Total chunks: {total_chunks}")
        
        return parsed_data
