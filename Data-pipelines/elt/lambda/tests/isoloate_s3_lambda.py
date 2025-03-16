import os
import logging
from datetime import datetime
import boto3
import json


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(module)s - %(funcName)s - %(pathname)s:%(lineno)d - %(message)s')

def lambda_handler(event, context):
    logging.info("Starting Lambda handler for S3 access test")

    s3_client = boto3.client('s3')
    bucket_name = os.environ['S3_BUCKET_NAME_TEXTRACT_JSON_RESPONSE']

    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        # Convert datetime objects to ISO format strings within the comprehension
        files_info = [{'Key': content['Key'], 'LastModified': content['LastModified'].isoformat()} for content in response.get('Contents', [])]

        logging.info(f"Files listed in bucket: {bucket_name}")
        # Serialize the entire response using json.dumps, ensuring all datetime objects are strings
        serialized_response = json.dumps({'status': 'success', 'data': files_info}, default=str)
        return serialized_response
    except Exception as e:
        logging.error(f"Error accessing S3 bucket {bucket_name}: {e}")
        serialized_error = json.dumps({'status': 'error', 'message': str(e)}, default=str)
        return serialized_error
