from flask import Blueprint, request, jsonify
from src.core.rag_engine import RAGEngine       
from src.core.data_layer.document_ingestion_service import DocumentIngestionService
from src.utils.logger import get_logger, time_function, log_function_call
from src.repositories.file_repository import FileRepository
from src.models.file_model import FileStatusEnum

logger = get_logger(__name__)
ingest_bp = Blueprint('ingest', __name__)

# Initialize the document ingestion service
ingestion_service = DocumentIngestionService()

@ingest_bp.route('/ingest', methods=['POST'])
@time_function
@log_function_call
def ingest():
    """Handle data source ingestion request for single file"""
    logger.info("Received ingest request")
    
    data = request.get_json()
    
    source_type = data.get('source_type', 's3')
    if not source_type:
        return jsonify({"error": "source_type is required"}), 400
    
    bucket_name = data.get('bucket_name')
    if not bucket_name:
        return jsonify({"error": "bucket_name is required"}), 400

    s3_object_key = data.get('s3_object_key')
    if not s3_object_key:
        return jsonify({"error": "s3_object_key is required"}), 400

    project_name = data.get('project_name', 'rag-engine')   
    if not project_name:
        return jsonify({"error": "project_name is required"}), 400
    
    try:
        # Create data source
        data_source = ingestion_service.create_data_source(source_type, bucket_name=bucket_name)
        
        # Process single file
        FileRepository().update_file_status(s3_object_key, FileStatusEnum.VALIDATION_IN_PROGRESS)
        documents = ingestion_service.process_file(data_source, s3_object_key)

        # Update file status to ingestion in progress
        FileRepository().update_file_status(s3_object_key, FileStatusEnum.INGESTION_IN_PROGRESS)
        # Ingest into vector DB
        ingestion_status = RAGEngine(project_name=project_name).ingest(documents, parallel_threads=5)
        # Update file status to available
        if ingestion_status:
            FileRepository().update_file_status(s3_object_key, FileStatusEnum.AVAILABLE)
        else:
            FileRepository().update_file_status(s3_object_key, FileStatusEnum.INGESTION_FAILED)
            return jsonify({"error": "Document ingestion failed"}), 500
        
        return jsonify({
            "status": "success", 
            "message": "Document ingested and vector DB updated.",
            "documents_processed": len(documents),
            "total_chunks": sum(len(doc['chunks']) for doc in documents),
            "source_type": source_type,
            "s3_object_key": s3_object_key
        })
        
    except Exception as e:
        logger.error(f"Error processing data source request: {str(e)}")
        return jsonify({"error": str(e)}), 500
    

@ingest_bp.route('/ingest/supported-formats', methods=['GET'])
def get_supported_formats():
    """Get list of supported file formats"""
    return jsonify({
        "supported_extensions": list(ingestion_service.supported_extensions),
        "supported_formats": [
            "PDF Documents (.pdf)",
            "Text Files (.txt, .md, .rst, .log)",
            "Structured Text (.json, .xml, .html, .htm)",
            "Word Documents (.docx, .doc)",
            "PowerPoint Presentations (.pptx, .ppt)"
        ],
        "excluded_formats": [
            "Images (jpg, png, gif, etc.)",
            "Videos (mp4, avi, mov, etc.)",
            "Spreadsheets (csv, xlsx, xls)",
            "Audio files (mp3, wav, etc.)"
        ]
    })