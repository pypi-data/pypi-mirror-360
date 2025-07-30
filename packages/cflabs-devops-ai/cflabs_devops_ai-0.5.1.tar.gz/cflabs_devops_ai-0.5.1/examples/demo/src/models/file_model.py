import enum
from sqlalchemy import Column, String, Enum as SQLAlchemyEnum, DateTime, BigInteger
from sqlalchemy.sql import func # For updated_at default server timestamp
from sqlalchemy.ext.declarative import declarative_base

# Assuming Base is defined in core.database and imported by the repository or handler
# For a standalone model file like this, if Base is not easily accessible for definition,
# you might need a placeholder or a way to late-bind it.
# For now, we'll assume it will be used with a Base from core.database
from src.database import Base # Relative import to access Base

class FileStatusEnum(str, enum.Enum):
    # Define only the statuses relevant to this Lambda
    # Or all statuses if they might be encountered or set
    PENDING_UPLOAD = "pending_upload"
    VALIDATION_IN_PROGRESS = "validation_in_progress"
    INGESTION_IN_PROGRESS = "ingestion_in_progress"
    AVAILABLE = "available"
    UPLOAD_FAILED = "upload_failed"
    VALIDATION_FAILED = "validation_failed"
    VALIDATION_ERROR = "validation_error"
    INGESTION_FAILED = "ingestion_failed"
    INGESTION_ERROR = "ingestion_error"

    # PENDING_SCAN = "pending_scan"
    # READY_FOR_INGESTION = "ready_for_ingestion"
    # SCAN_IN_PROGRESS = "scan_in_progress"
    # AVAILABLE = "available" 
    # UPLOAD_FAILED = "upload_failed"
    # VALIDATION_FAILED = "validation_failed"
    # VALIDATION_ERROR = "validation_error"
    # Add other statuses from your main application if needed for robust checks
    # UPLOADING = "uploading" 
    # SCANNING = "scanning"
    # SCAN_FAILED = "scan_failed"
    # INFECTED = "infected"
    # PENDING_EXTRACTION = "pending_extraction"
    # EXTRACTING = "extracting"
    # EXTRACTION_FAILED = "extraction_failed"
    # DELETION_PENDING = "deletion_pending"


class FileModel(Base):
    __tablename__ = "files" # Match your existing table name

    # Define only the columns needed for the Lambda operation
    # The primary key for lookup (e.g., s3_object_key or luid if passed in event metadata)
    # And the columns to be updated (status, updated_at)
    
    # Assuming 'luid' is the primary key defined in your BaseModel equivalent
    # If not, and you use 'id' (integer), define it here.
    luid = Column(String(36), primary_key=True) # Assuming luid is String(36) UUID
    s3_object_key = Column(String(1024), unique=True, nullable=False, index=True) # Max key length for S3 is 1024
    original_filename = Column(String(255), nullable=True) # Added field
    name = Column(String(255), nullable=True) # Added field for cleaned name
    size_bytes = Column(BigInteger, nullable=True) # Added field for file size
    status = Column(SQLAlchemyEnum(FileStatusEnum, native_enum=True), nullable=False, default=FileStatusEnum.PENDING_UPLOAD)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    project_id = Column(String(36), nullable=True) # Added field for project ID
    ingested_table_name = Column(String(255), nullable=True) # Added field for ingested table name
    ingested_db_name = Column(String(255), nullable=True) # Added field for ingested db name

    # Minimal representation: Add other columns only if directly used by the Lambda
    # for conditions or logging in a way that can't be avoided.

    def __repr__(self):
        return f"<FileModel(luid='{self.luid}', s3_key='{self.s3_object_key}', status='{self.status.value}', original_filename='{self.original_filename}', size='{self.size_bytes}')>" 