""" Refactoring AWS Textract Call Cadence"""

import os
import json
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import boto3
from botocore.exceptions import ClientError

# Configure logging level
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

# Initialize the S3 and Textract clients outside of the handler for reuse
s3_client = boto3.client('s3')
textract_client = boto3.client('textract')

def lambda_handler(event, context):
    """ 
    Processes invoices in parallel from an S3 bucket using Textract,
    handling multiple concurrent requests and tracking results.
    """
    # Retrieve the bucket names from environment variables
    invoice_bucket = os.environ['S3_BUCKET_NAME_INVOICE']
    textract_bucket = os.environ['S3_BUCKET_NAME_TEXTRACT_JSON_RESPONSE']
    
    # Maximum number of concurrent Textract calls
    max_concurrent_textract_calls = int(os.getenv('MAX_CONCURRENT_TEXTRACT_CALLS', '5'))
    
    # Retrieve all objects (invoices) from Folder A in the invoice bucket
    invoices = list_invoices(invoice_bucket)
    if not invoices:
        return {'statusCode': 200, 'body': 'No invoices found in Folder A'}

    # Process invoices in parallel
    with ThreadPoolExecutor(max_workers=max_concurrent_textract_calls) as executor:
        future_to_invoice = {executor.submit(process_invoice, invoice, invoice_bucket, textract_bucket): invoice for invoice in invoices}
        
        for future in as_completed(future_to_invoice):
            invoice = future_to_invoice[future]
            try:
                future.result()
                logger.info(f"Invoice {invoice['Key']} processed successfully")
            except Exception as e:
                logger.error(f"Invoice {invoice['Key']} failed to process: {str(e)}")

    return {'statusCode': 200, 'body': 'PDF invoices processed'}

def list_invoices(bucket_name, prefix='invoices/Folder-A/'):
    """List invoices in the specified S3 bucket and prefix."""
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        return response.get('Contents', [])
    except ClientError as e:
        logger.error(f"ClientError in listing objects in {prefix}: {e.response['Error']['Message']}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in listing objects in {prefix}: {str(e)}")
        raise

def process_invoice(invoice, invoice_bucket, textract_bucket):
    """Process a single invoice, including Textract analysis and moving files in S3."""
    object_key = invoice['Key']
    filename = object_key.split('/')[-1]
    folder_path = '/'.join(object_key.split('/')[2:])

    # Move the PDF file from Folder A to Folder B
    move_s3_object(invoice_bucket, object_key, f'invoices/Folder-B/{folder_path}')

    # Start Textract analysis
    job_id = start_textract_analysis(invoice_bucket, f'invoices/Folder-B/{folder_path}', filename)

    # Get Textract results
    textract_result = get_expense_analysis_with_retry(textract_client, job_id)

    # Save Textract results to S3
    save_textract_results(textract_bucket, f'invoices/Folder-A/{folder_path}.json', textract_result)

    # Move the PDF file from Folder B to Folder C
    move_s3_object(invoice_bucket, f'invoices/Folder-B/{folder_path}', f'invoices/Folder-C/{folder_path}')

def move_s3_object(bucket_name, source_key, destination_key):
    """Move an object within the same S3 bucket."""
    try:
        s3_client.copy_object(CopySource={'Bucket': bucket_name, 'Key': source_key}, Bucket=bucket_name, Key=destination_key)
        s3_client.delete_object(Bucket=bucket_name, Key=source_key)
    except ClientError as e:
        logger.error(f"ClientError in moving S3 object from {source_key} to {destination_key}: {e.response['Error']['Message']}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in moving S3 object from {source_key} to {destination_key}: {str(e)}")
        raise

def start_textract_analysis(bucket_name, object_key, filename):
    """Start Textract expense analysis and return the job ID."""
    try:
        response = textract_client.start_expense_analysis(
            DocumentLocation={
                'S3Object': {'Bucket': bucket_name, 'Name': object_key}
            }
        )
        return response['JobId']
    except ClientError as e:
        logger.error(f"ClientError in start_expense_analysis for {filename}: {e.response['Error']['Message']}")
        raise
    except Exception as e:
        logger.error(f"Failed to start expense analysis for {filename}: {str(e)}")
        raise

def get_expense_analysis_with_retry(client, job_id, max_attempts=5):
    """Retrieve the Textract analysis result with retries."""
    for attempt in range(max_attempts):
        try:
            time.sleep(2 ** attempt)  # Exponential backoff
            response = client.get_expense_analysis(JobId=job_id)
            if response['JobStatus'] == 'SUCCEEDED':
                return response
            elif response['JobStatus'] == 'FAILED':
                logger.error(f"Textract processing failed for JobId {job_id}")
                raise Exception('Textract processing failed')
        except ClientError as e:
            logger.error(f"ClientError in get_expense_analysis for JobId {job_id}: {e.response['Error']['Message']}")
            if attempt >= max_attempts - 1:
                raise
        except Exception as e:
            logger.error(f"Unexpected error in get_expense_analysis for JobId {job_id}: {str(e)}")
            if attempt >= max_attempts - 1:
                raise
    raise Exception('Timeout: Textract processing took too long or exceeded retry attempts')

def save_textract_results(bucket_name, object_key, textract_result):
    """Save Textract results to S3."""
    try:
        json_response = json.dumps(textract_result)
        s3_client.put_object(Bucket=bucket_name, Key=object_key, Body=json_response)
    except ClientError as e:
        logger.error(f"ClientError in saving JSON response to S3 for {object_key}: {e.response['Error']['Message']}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in saving JSON response to S3 for {object_key}: {str(e)}")
        raise