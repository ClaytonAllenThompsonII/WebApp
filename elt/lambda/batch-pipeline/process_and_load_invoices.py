import json
import boto3
import psycopg2
import os

# Initialize the S3 client outside of the handler for potential reuse
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    Main handler for processing and loading invoice data.
    Triggered by EventBridge, it processes accumulated JSON files from S3,
    loads them into a PostgreSQL staging table, and triggers downstream processing.
    """
    bucket_name = os.environ['S3_BUCKET_NAME_TEXTRACT_JSON_RESPONSE']  # Replace with your bucket name
    processed_prefix = 'processed/'  # Prefix for processed files

    # Establish RDS database connection
    conn = psycopg2.connect(
        dbname=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'], 
        host=os.environ['DB_HOST'],
        port=os.environ['DB_PORT']
    )

    # Process JSON files from S3 and load into the staging table
    process_json_files(conn, bucket_name, processed_prefix)

    # Trigger stored procedure for downstream processing
    trigger_stored_procedure(conn)

    # Close the database connection
    conn.close()

def process_json_files(conn, bucket_name, processed_prefix):
    """
    Retrieves JSON files from S3, excluding those in the processed prefix,
    and loads their content into the PostgreSQL staging table.
    """
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    if 'Contents' in response:
        for item in response['Contents']:
            key = item['Key']
            if not key.startswith(processed_prefix):  # Skip processed files
                json_data = s3_client.get_object(Bucket=bucket_name, Key=key)['Body'].read()
                load_json_to_staging(conn, json_data)

                # Optionally move the file to the processed folder
                move_file_to_processed(bucket_name, key, processed_prefix)

def load_json_to_staging(conn, json_data):
    """
    Inserts JSON data into the PostgreSQL staging table.
    """
    cursor = conn.cursor()
    insert_query = "INSERT INTO invoice_processing_staging (data, processed) VALUES (%s, FALSE)"
    cursor.execute(insert_query, (json_data,))
    conn.commit()
    cursor.close()

def trigger_stored_procedure(conn):
    """
    Calls the stored procedure in PostgreSQL that initiates downstream processing.
    """
    cursor = conn.cursor()
    cursor.callproc('process_invoice_data')  # Adjust to your stored procedure name
    conn.commit()
    cursor.close()

def move_file_to_processed(bucket, key, processed_prefix):
    """
    Moves a processed file to the 'processed' prefix within the same S3 bucket.
    """
    new_key = processed_prefix + key
    s3_client.copy_object(Bucket=bucket, CopySource={'Bucket': bucket, 'Key': key}, Key=new_key)
    s3_client.delete_object(Bucket=bucket, Key=key)
