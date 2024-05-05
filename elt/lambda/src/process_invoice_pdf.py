
import os
import json
import time
import logging
import boto3
from botocore.exceptions import ClientError

# Configure logging level
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

def lambda_handler(event, context):
    # Initialize the S3 client
    s3_client = boto3.client('s3')

    # Retrieve the bucket names
    invoice_bucket = os.environ['S3_BUCKET_NAME_INVOICE']
    textract_bucket = os.environ['S3_BUCKET_NAME_TEXTRACT_JSON_RESPONSE']

    # Retrieve all objects (invoices) from Folder A in the invoice bucket
    try:
        response = s3_client.list_objects_v2(
            Bucket=invoice_bucket,
            Prefix='invoices/Folder-A/'
        )
        if 'Contents' not in response:
            logger.info("No invoices found in Folder A")
            return {
                'statusCode': 200,
                'body': 'No invoices found in Folder A'
            }
        else:
            invoices = response['Contents']
    except ClientError as e:
        logger.error(f"ClientError in listing objects in Folder A: {e.response['Error']['Message']}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in listing objects in Folder A: {str(e)}")
        raise

    # Initialize the Textract client
    textract_client = boto3.client('textract')

    # Process each invoice
    for invoice in invoices:
        object_key = invoice['Key']

        # Extract filename from the object key
        filename = object_key.split('/')[-1]
        folder_path = '/'.join(object_key.split('/')[2:])  # Preserve {group}/user_{user_id}/{file.name} structure


        try:
            # Move the PDF file from Folder A to Folder B
            s3_client.copy_object(
                CopySource={'Bucket': invoice_bucket, 'Key': object_key},
                Bucket=invoice_bucket,
                Key=f'invoices/Folder-B/{folder_path}'
            )
            # Delete the original PDF file from Folder A
            s3_client.delete_object(Bucket=invoice_bucket, Key=object_key)
        except ClientError as e:
            logger.error(f"ClientError in moving PDF file from Folder A to Folder B: {e.response['Error']['Message']}")
            continue  # Move to the next invoice
        except Exception as e:
            logger.error(f"Unexpected error in moving PDF file from Folder A to Folder B: {str(e)}")
            continue  # Move to the next invoice

        try:
            # Invoke Textract's start_expense_analysis method on the uploaded PDF in Folder B
            response = textract_client.start_expense_analysis(
                DocumentLocation={
                    'S3Object': {
                        'Bucket': invoice_bucket,
                        'Name': f'invoices/Folder-B/{folder_path}'
                    }
                }
            )
            # Retrieve the job ID from the start response
            job_id = response['JobId']
        except ClientError as e:
            logger.error(f"ClientError in start_expense_analysis for {filename}: {e.response['Error']['Message']}")
            continue  # Move to the next invoice
        except Exception as e:
            logger.error(f"Failed to start expense analysis for {filename} in {invoice_bucket}: {str(e)}")
            continue  # Move to the next invoice

        # Wait for Textract analysis to complete
        try:
            textract_result = get_expense_analysis_with_retry(textract_client, job_id)
        except Exception as e:
            logger.error(f"Failed to get Textract results for {filename}: {str(e)}")
            continue  # Move to the next invoice

        # Extract the JSON response from the Textract Dictionary result
        json_response = json.dumps(textract_result)

        # Move the JSON response to Folder A in the textract bucket
        try:
            s3_client.put_object(
                Bucket=textract_bucket,
                Key=f'invoices/Folder-A/{folder_path}.json',
                Body=json_response
            )
        except ClientError as e:
            logger.error(f"ClientError in saving JSON response to S3 for {filename}: {e.response['Error']['Message']}")
            continue  # Move to the next invoice
        except Exception as e:
            logger.error(f"Unexpected error in saving JSON response to S3 for {filename}: {str(e)}")
            continue  # Move to the next invoice

        # Move the PDF file from Folder B to Folder C
        try:
            # Copy the object from Folder B to Folder C
            s3_client.copy_object(
                CopySource={'Bucket': invoice_bucket, 'Key': f'invoices/Folder-B/{folder_path}'},
                Bucket=invoice_bucket,
                Key=f'invoices/Folder-C/{folder_path}'
            )
            # Delete the original PDF file from Folder B
            s3_client.delete_object(Bucket=invoice_bucket, Key=f'invoices/Folder-B/{folder_path}')
        except ClientError as e:
            logger.error(f"ClientError in moving PDF file from Folder B to Folder C: {e.response['Error']['Message']}")
            continue  # Move to the next invoice
        except Exception as e:
            logger.error(f"Unexpected error in moving PDF file from Folder B to Folder C: {str(e)}")
            continue  # Move to the next invoice

        logger.info(f"Invoice {filename} processed successfully")

    return {
        'statusCode': 200,
        'body': 'PDF invoices processed successfully'
    }


def get_expense_analysis_with_retry(textract_client, job_id, max_attempts=5):
    """
    Retrieves the Textract expense analysis result with retry logic.

    Implements an exponential backoff strategy for retries to handle transient errors or rate limiting
    by the Textract service. This function polls the Textract service for the completion of the expense
    analysis job and returns the result once the job succeeds.

    Parameters:
    - textract_client (boto3.client): A Boto3 Textract client.
    - job_id (str): The job identifier for the Textract expense analysis request.
    - max_attempts (int): Maximum number of retry attempts. Default is 5.

    Returns:
    - dict: The JSON response from Textract containing the analysis result once the job status is 'SUCCEEDED'.

    Raises:
    - Exception: If the job status is 'FAILED', if all retry attempts are exhausted without success,
      or if an unexpected error occurs.
    """

    for attempt in range(max_attempts):
        try:
            # Wait before retrying using exponential backoff strategy
            time.sleep(2 ** attempt)  # Exponential backoff
            # Poll the Textract job status
            response = textract_client.get_expense_analysis(JobId=job_id)
            status = response['JobStatus']

            if status == 'SUCCEEDED':
                # Job succeeded, return the analysis result
                return response
            elif status == 'FAILED':
                # Job failed, log and raise an exception
                logger.error(f"Textract processing failed for JobId {job_id}")
                raise Exception('Textract processing failed')
        except ClientError as e:
            # Handle client errors from the Textract service, such as rate limits or other service issues
            logger.error(f"ClientError in get_expense_analysis for JobId {job_id}: {e.response['Error']['Message']}")
            if attempt >= max_attempts - 1:
                # Exhausted all attempts, re-raise the exception
                raise
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error in get_expense_analysis for JobId {job_id}: {str(e)}")
            if attempt >= max_attempts - 1:
                # Exhausted all attempts, re-raise the exception
                raise
    # If the loop completes without returning or raising an exception for 'SUCCEEDED' status, raise a timeout exception
    raise Exception('Timeout: Textract processing took too long or exceeded retry attempts')