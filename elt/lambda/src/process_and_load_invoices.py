"""
Phase 2 of Lambda Development for Automated Invoice Processing.

This Lambda function is designed to automate the processing of invoice data stored in JSON files within an AWS S3 bucket. 
Triggered by AWS EventBridge at a scheduled time, it performs the following operations:
1. Retrieves JSON files containing invoice data from an S3 bucket, excluding those already processed.
2. Loads the data from these files into a PostgreSQL staging table in a batch-wise manner for efficiency.
3. Triggers a stored procedure in the PostgreSQL database for downstream processing of the loaded data.
4. Moves processed files to a 'processed/' prefix within the S3 bucket to prevent reprocessing.

This automation streamlines the ingestion and initial processing of invoice data, preparing it for further analysis or application use.
"""
import os
import boto3
import psycopg2


# Initialize the S3 client outside of the handler for potential reuse
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    Main handler for processing and loading invoice data into PostgreSQL and initiating downstream processing..
    """
    # Retrieve environment variables for S3 bucket name and processed file prefix
    bucket_name = os.environ['S3_BUCKET_NAME_TEXTRACT_JSON_RESPONSE']
    processed_prefix = 'processed/'  # Prefix indicating where processed files are moved.

    # Establish a connection to the PostgreSQL RDS instance
    conn = psycopg2.connect(
        dbname=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        host=os.environ['DB_HOST'],
        port=os.environ['DB_PORT']
    )

    # Step 1: Process JSON files from S3 and load them into the staging table
    process_json_files(conn, bucket_name, processed_prefix)

    # Step 2: After loading, trigger stored procedure for further data manipulation and downstream processing
    trigger_stored_procedure(conn)

    # Close the database connection to clean up resources
    conn.close()

def process_json_files(conn, bucket_name, processed_prefix):
    """
    Retrieves and processes JSON files from S3, excluding those in the processed/ prefix,
    and loads their content into the PostgreSQL staging table in batches.
    """
    # List objects in the specified S3 bucket
    response = s3_client.list_objects_v2(Bucket=bucket_name)
    batch_size = 10 # Define the batch size for processing
    data_batch = [] # Initialize an empty list to hold data for batch processing
    processed_files = [] # Track files that have been processed

    # Check if the response contains any contents
    if 'Contents' in response:
        for item in response['Contents']:
            key = item['Key']
            # Skip files that have already been processed
            if not key.startswith(processed_prefix):  # Skip processed files
                # Retrieve and decode the JSON data from S3. 
                json_data = s3_client.get_object(Bucket=bucket_name, Key=key)['Body'].read() # The response from get_object is a dict that contains several fields, including: 'Body'. 
                # Decode the JSON data from bytes to string
                json_data_str = json_data.decode('utf-8')

                # Append file data to the batch list
                data_batch.append((key, json_data_str))

                # When the batch reaches the specified size, process it
                if len(data_batch) >= batch_size:
                    load_json_to_staging_batch(conn, data_batch)
                    processed_files.extend(data_batch)  # Keep track of processed files
                    data_batch = []  # Reset the batch

        # Process remaining files in the batch
        if data_batch:
            load_json_to_staging_batch(conn, data_batch)
            processed_files.extend(data_batch)

        # Move processed files after all batches are processed
        for key, _ in processed_files:
            move_file_to_processed(bucket_name, key, processed_prefix) 


def load_json_to_staging_batch(conn,data_batch):
    """
    Inserts JSON data into the PostgreSQL staging table.
    """
    cursor = conn.cursor()
    # Ensure the column name matches your table's schema
    # Updated INSERT query to match the table schema
    insert_query = """
    INSERT INTO in_invoice_processing (s3_object_key, textract_json, processed)
    VALUES (%s, %s, FALSE)
    """
    # Execute the batch insert operation
    cursor.executemany(insert_query, data_batch)
    conn.commit() # Commit the transaction to make changes permanent
    cursor.close() # Close the cursor to release PostgreSQL resources

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
    Moves a processed file to the 'processed/' prefix within the same S3 bucket.
    """
    new_key = processed_prefix + key
    s3_client.copy_object(Bucket=bucket, CopySource={'Bucket': bucket, 'Key': key}, Key=new_key)
    s3_client.delete_object(Bucket=bucket, Key=key)
