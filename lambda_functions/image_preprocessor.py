"""
AWS Lambda function for image preprocessing.

This module contains the lambda_handler function that is triggered by an S3 event.
It processes the image uploaded to S3 by resizing it and then uploads the processed
image back to a different S3 bucket. The function uses Boto3 for AWS interactions
and Pillow for image processing.
"""
import uuid
import logging
import boto3
from PIL import Image


# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')

def resize_image(image_path, resized_path):
    """
    Resizes an image to a specified size.

    Args:
    - image_path (str): The path to the source image.
    - resized_path (str): The path to save the resized image.
    """
    try:
        with Image.open(image_path) as image:
            image = image.resize((1280, 720))  # Example resize; adjust as needed
            image.save(resized_path)
        logger.info(f"Image resized and saved to {resized_path}")
    except Exception as e:
        logger.error(f"Error in resizing image: {e}")
        raise

def lambda_handler(event, context):
    """
    AWS Lambda function handler.

    Processes each record in the S3 event. It resizes the image and uploads it
    back to a specified S3 bucket.

    Args:
    - event: AWS event containing the S3 object information.
    - context: AWS runtime information.
    """
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']
        download_path = f'/tmp/{uuid.uuid4()}{key}'
        upload_path = f'/tmp/resized-{key}'

        try:
            logger.info(f"Downloading image {key} from bucket {bucket}")
            s3_client.download_file(bucket, key, download_path)

            logger.info("Resizing image")
            resize_image(download_path, upload_path)

            logger.info(f"Uploading resized image to bucket your-resized-image-bucket")
            s3_client.upload_file(upload_path, 'your-resized-image-bucket', key)
        except Exception as e:
            logger.error(f"Error processing {key}: {e}")
            raise

        logger.info(f"Processing complete for {key}")