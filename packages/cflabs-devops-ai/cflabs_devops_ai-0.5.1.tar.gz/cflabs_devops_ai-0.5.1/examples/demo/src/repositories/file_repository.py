from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from src.models.file_model import FileModel, FileStatusEnum # Assuming absolute import is correct for your structure
from src.utils.logger import get_logger

logger = get_logger(__name__)

class FileRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def find_by_s3_key(self, s3_key: str) -> Optional[FileModel]:
        """Finds a file record by its S3 object key."""
        try:
            return self.db_session.query(FileModel).filter(FileModel.s3_object_key == s3_key).first()
        except Exception as e:
            logger.error(f"Error finding file by s3_key '{s3_key}': {e}", exc_info=True)
            # Consider re-raising a custom repository exception if the caller needs to handle DB errors specifically
            return None

    def update_file_attributes(
        self,
        s3_key: str,
        attributes_to_update: Dict[str, Any]
    ) -> Optional[FileModel]:
        """
        Updates specified attributes of a file record identified by its S3 object key.

        Args:
            s3_key: The S3 object key of the file.
            attributes_to_update: A dictionary where keys are attribute names of FileModel
                                  (e.g., "status", "original_filename", "size_bytes", "validation_notes")
                                  and values are the new values for these attributes.
                                  Example: {"status": FileStatusEnum.PENDING_SCAN, "size_bytes": 1024}

        Returns:
            The updated FileModel object if successful, None otherwise.
        """
        try:
            logger.debug(f"Attempting to update attributes for S3 key: {s3_key} with data: {attributes_to_update}")
            file_record = self.find_by_s3_key(s3_key)

            if not file_record:
                logger.warning(f"File with S3 key '{s3_key}' not found. Cannot update attributes.")
                return None

            updated = False
            for key, value in attributes_to_update.items():
                if hasattr(file_record, key):
                    current_value = getattr(file_record, key)
                    if current_value != value:
                        setattr(file_record, key, value)
                        updated = True
                        logger.debug(f"Attribute '{key}' for S3 key '{s3_key}' changed from '{current_value}' to '{value}'.")
                else:
                    logger.warning(f"Attribute '{key}' not found in FileModel for S3 key '{s3_key}'. Skipping update for this attribute.")
            
            if updated:
                self.db_session.commit()
                logger.info(f"Successfully updated attributes for S3 key '{s3_key}'.")
            else:
                logger.info(f"No attributes needed updating for S3 key '{s3_key}' based on provided data.")
            
            return file_record
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"Error updating attributes for S3 key '{s3_key}': {e}", exc_info=True)
            return None

    # You can keep your existing update_status_by_s3_key if it's heavily used elsewhere,
    # or refactor its callers to use update_file_attributes.
    # The new method update_file_attributes is more generic.

    # Example of how your previous method could be implemented using the new one (for compatibility):
    def update_status_by_s3_key_legacy(
        self,
        s3_key: str,
        new_status: FileStatusEnum,
        original_filename: Optional[str] = None,
        size_bytes: Optional[int] = None,
        # current_expected_status: Optional[FileStatusEnum] = None # This check would now be done in the service layer/handler
    ) -> Optional[FileModel]:
        """
        Legacy wrapper. Updates status, original_filename, and size_bytes.
        Note: The current_expected_status check is better handled in the calling code (handler/service)
        before calling a generic update method.
        """
        attributes_to_update = {"status": new_status}
        if original_filename is not None:
            attributes_to_update["original_filename"] = original_filename
        if size_bytes is not None:
            attributes_to_update["size_bytes"] = size_bytes
        
        # The check for current_expected_status should ideally be done *before* calling this
        # to decide IF an update should even be attempted.
        # If you must keep it here, you'd fetch the record first, check, then call update_file_attributes.

        return self.update_file_attributes(s3_key, attributes_to_update)

    # More specific methods for clarity in the handler:

    def update_initial_file_details(
        self,
        s3_key: str,
        new_status: FileStatusEnum,
        original_filename: str,
        size_bytes: Optional[int], # Size might not always be available
        project_id: Optional[str] # Added project_id
    ) -> Optional[FileModel]:
        """
        Specific method for the initial update after S3 object creation.
        This updates status, original_filename, size_bytes, and project_id.
        """
        attributes = {
            "status": new_status,
            "original_filename": original_filename
        }
        if size_bytes is not None:
            attributes["size_bytes"] = size_bytes
        if project_id is not None: # Add project_id to attributes if provided
            attributes["project_id"] = project_id
        
        return self.update_file_attributes(s3_key, attributes)

    def update_validation_outcome(
        self,
        s3_key: str,
        validation_status: FileStatusEnum,
        validation_notes: Optional[str] = None # Assuming you might add this to your FileModel
    ) -> Optional[FileModel]:
        """
        Specific method to update status and potentially notes after validation.
        """
        attributes = {"status": validation_status}
        # if validation_notes is not None and hasattr(FileModel, "validation_notes"): # Check if model has the field
        #     attributes["validation_notes"] = validation_notes
        
        return self.update_file_attributes(s3_key, attributes)
    

    def project_has_data(self, project_id: str) -> bool:
        """
        Checks if the project DB (i.e., project-related data) is present.
        """
        return self.db_session.query(FileModel).filter(FileModel.project_id == project_id).first() is not None