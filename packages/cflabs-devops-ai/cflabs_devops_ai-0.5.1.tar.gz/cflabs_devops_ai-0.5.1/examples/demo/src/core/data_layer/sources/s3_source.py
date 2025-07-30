import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from typing import BinaryIO
from io import BytesIO
from src.base_classes.data_layer_class import DataSource
from src.utils.logger import get_logger

logger = get_logger(__name__)

class S3DataSource(DataSource):
    """Data source for AWS S3"""
    
    def __init__(self, bucket_name: str):
        self.bucket_name = bucket_name
        
        # Initialize S3 client
        try:
            self.s3_client = boto3.client('s3')
            logger.info(f"Initialized S3DataSource for bucket: {bucket_name}")
        except NoCredentialsError:
            raise Exception("AWS credentials not found. Please configure AWS credentials.")
    
    def get_file(self, file_path: str) -> BinaryIO:
        """Retrieve a file from S3"""
        try:
            logger.debug(f"Downloading file from S3: {file_path}")
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_path)
            return BytesIO(response['Body'].read())
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                raise FileNotFoundError(f"File not found in S3: {file_path}")
            else:
                raise Exception(f"Error accessing S3 file {file_path}: {str(e)}")
    
    def file_exists(self, file_path: str) -> bool:
        """Check if a file exists in S3 bucket"""
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=file_path)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            else:
                raise Exception(f"Error checking S3 file existence: {str(e)}") 