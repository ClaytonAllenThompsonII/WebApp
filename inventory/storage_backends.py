"""
AWS Storage Backend Module

This module provides a backend interface for interacting with AWS S3 and DynamoDB services.
It facilitates the upload of files to S3 and the creation of inventory items in DynamoDB. The 
primary use case is handling image storage and metadata management for an inventory processing system.

Classes:
    AWSStorageBackend: Handles S3 file uploads and DynamoDB item creation.

Requirements:
    - boto3: AWS SDK for Python.
    - AWS credentials and region settings configured in Django settings or environment variables.
"""
from datetime import datetime
import os
import uuid
import logging
from botocore.config import Config
from django.conf import settings
import boto3


# logger instance
logger = logging.getLogger(__name__)


class AWSStorageBackend:
    """ Handles interactions with AWS S3 for image storage."""
    def __init__(self) -> None:
        """Initialize the S3 client using environment variables for credentials""" 
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
                config=Config(signature_version='s3v4')
                )
            logger.debug(f"Initialized S3 client with region: {settings.AWS_REGION}")
            
    

            # Bucket name from environment or settings
            self.bucket_name = os.environ['S3_BUCKET_NAME'] # user image upload bucket
            logger.info("AWS S3 client initialized successfully.")  

        except Exception as e:
            logger.error("Error initializing AWS clients: %s", e)
            raise


    def upload_file(self, file, user_id, group_id, cycle_id) -> str:
        """
        Uploads a file-like object to S3 and returns the generated S3 key.
        
        The S3 key follows the pattern:
            inventory/group_<group_id>/user_<user_id>/cycle_<cycle_id>/YYYY/MM/DD/<uuid>.<ext>
        
        Parameters:
            file: A file-like object (e.g., from request.FILES).
            user_id: The ID of the user uploading the file.
            group_id: The ID of the group (e.g., restaurant business) to which the user belongs.
            cycle_id: The inventory cycle ID associated with this upload.
        
        Returns:
            The S3 object key (string) for the uploaded file.
        """
        # Create a date-based folder (e.g., "2025/03/22")
        date_str = datetime.now().strftime("%Y/%m/%d")
        # Get the file extension (e.g., ".jpg")
        ext = os.path.splitext(file.name)[1] or ''
        # Generate a unique identifier
        unique_id = str(uuid.uuid4())
        
        # Build the S3 key using the required hierarchy
        s3_key = f"inventory/group_{group_id}/user_{user_id}/cycle_{cycle_id}/{date_str}/{unique_id}{ext}"
        
        logger.debug(f"Attempting to upload file to S3 with key: {s3_key}")
        
        try:
            self.s3_client.upload_fileobj(file, self.bucket_name, s3_key)
            logger.info(f"File successfully uploaded to S3: {s3_key}")
            return s3_key
        except Exception as e:
            logger.error(f"Error occurred during file upload to S3: {e}")
            raise Exception(f"Error uploading file to S3: {e}") from e
    

   