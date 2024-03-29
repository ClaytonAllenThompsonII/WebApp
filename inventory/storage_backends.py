""" Add Module Doc String"""
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
    """Handles interactions with AWS S3 and DynamoDB for image storage and metadata management."""
    def __init__(self) -> None:
        """Initialize the S3 and DynamoDB clients using environment variables for credentials""" 
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION,
                config=Config(signature_version='s3v4')
                )
            logger.debug(f"Initialized S3 client with region: {settings.AWS_REGION}")
            
            self.dynamodb_client = boto3.client(
                'dynamodb',
                region_name=settings.AWS_REGION
                )
            logger.debug(f"Initialized DynamoDB client with region: {settings.AWS_REGION}")

            #set bucket and table names from environment variables
            self.bucket_name = os.environ['S3_BUCKET_NAME'] # user image upload bucket  
            self.table_name = os.environ['DYNAMODB_TABLE_NAME'] # image label bucket

            logger.info("AWS clients for S3 and DynamoDB initialized successfully")
        except Exception as e:
            logger.error("Error initializing AWS clients: %s", e)
            raise


    def upload_file(self, file, user_id):
        """Uploads a file to S3 and returns the generated filename"""
        # Format the current timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        # Extract the file extension
        file_extension = os.path.splitext(file.name)[1]
        # Construct the filename string
        filename = f"images/user_{user_id}_{timestamp}_{uuid.uuid4()}{file_extension}"

        logger.debug(f"Attempting to upload file {filename} to S3")

        print("Attempting to upload file to S3:", filename) # Debug print
    
        try:
            self.s3_client.upload_fileobj(file, self.bucket_name, filename)
            # Logging successful upload
            logger.info(f"File {filename} successfully uploaded to S3")
            print("File successfully uploaded to S3:", filename) # Debug Print
            return filename
        except Exception as e:
            logger.error(f"Error occurred during file upload to S3: {e}")
            print("Error occured during file upload to S3:", e) # Debug print
            raise Exception(f'Error uploading file to S3: {e}') from e 
            #will add less generic exception handling eventually. 
    

    def create_inventory_item(self, item_data):
        """Creates an item in the DynamoDB table with the provided data
        - Calls the put_item method on the DynamoDB client instance -> responsible for
        creating or updating single item in DynamoDB table.
        - Specifies the name of the DynamoDB table where the item should be stored.
        - This value is retrieved from the environment variable DYNAMO_TABLE_NAME.
         Provides the actual data to be inserted into the item. It's a dictionary containing
          the attribute name and values from the new item. 
        """
        print("Attempting to successfully upload to dynamoDB:", item_data, self.table_name)
        try:
            self.dynamodb_client.put_item(TableName=self.table_name, Item=item_data)
            print("Item_data successfully uploaded to dynamoDB:", item_data, self.table_name)
        except Exception as e: 
            raise Exception(f'Error creating item in DynamopDB: {e}') from e
            #will add less generic exception handling eventually. 

