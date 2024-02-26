import os
import boto3
from botocore.client import Config
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class S3StorageBackend:
    """Handles interactions with AWS S3 for invoice file storage."""
    def __init__(self):
        """Initialize the S3 client using environment variables for credentials."""
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
                config=Config(signature_version='s3v4')
            )
            logger.debug(f"Initialized S3 client with region: {settings.AWS_REGION}")


            #set bucket and table names from environment variables
            self.bucket_name = os.environ['S3_BUCKET_NAME_INVOICE'] # user PDF upload bucket

            logger.info("AWS clients for S3 and DynamoDB initialized successfully") 

        except Exception as e:
            logger.error("Error initializing S3 client: %s", e)
            raise

    def invoice_file_upload(self, file, user_id):
        """Uploads the invoice file to S3."""
        #file_extension = os.path.splitext(file.name)[1]
        # Generate the S3 key for the file
        s3_key = f'invoices/user_{user_id}/{file.name}'

        # Generate a unique filename or use the original filename
        filename = f'{user_id}_{file.name}'
        logger.debug(f"Attempting to upload file {filename} to S3")

        try:
            # Upload the file to S3
            self.s3_client.upload_fileobj(file, self.bucket_name, s3_key)
            logger.info(f"Invoice file '{filename}' uploaded to S3 successfully.")

            return filename
        except Exception as e:
            logger.error(f"Error uploading invoice file to S3: {e}")
            raise e
        