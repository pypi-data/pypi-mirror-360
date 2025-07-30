import PyPDF2
import uuid
from src.utils.logger import get_logger, time_function, log_function_call

logger = get_logger(__name__)

@time_function
@log_function_call
def create_documents_from_pdf(file, pages_per_doc=2):
    logger.info(f"Creating documents from PDF with {pages_per_doc} pages per document")
    
    reader = PyPDF2.PdfReader(file)
    num_pages = len(reader.pages)
    logger.info(f"PDF has {num_pages} pages")
    
    documents = []
    doc_id_base = str(uuid.uuid4())
    
    for i in range(0, num_pages, pages_per_doc):
        text = ""
        for j in range(i, min(i + pages_per_doc, num_pages)):
            text += reader.pages[j].extract_text() or ""
        
        doc_id = f"{doc_id_base}_{i//pages_per_doc}"
        documents.append({
            "doc_id": doc_id,
            "original_uuid": doc_id,
            "content": text,
            "page_start": i + 1,
            "page_end": min(i + pages_per_doc, num_pages),
            "file_id": file.filename,
        })
    
    logger.info(f"Created {len(documents)} documents from PDF")
    return documents

@time_function
@log_function_call
def chunk_document(document, chunk_size=300, overlap=50):
    logger.info(f"Chunking document {document['doc_id']} with chunk_size={chunk_size}, overlap={overlap}")
    
    text = document["content"]
    chunks = []
    start = 0
    chunk_id = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk_text = text[start:end]
        chunks.append({
            "chunk_id": f"{document['doc_id']}_{chunk_id}",
            "original_index": chunk_id,
            "content": chunk_text
        })
        chunk_id += 1
        start += chunk_size - overlap
    document["chunks"] = chunks
    return document
