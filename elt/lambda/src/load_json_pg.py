"""
Module: s3_to_postgres
Description: This module contains functions for transferring JSON files from an S3 bucket to a PostgreSQL database.
"""

import os
import logging
import json
import boto3
import psycopg2

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s - %(module)s - %(funcName)s - %(pathname)s:%(lineno)d - %(message)s')

# Initialize the S3 client outside of the handler for potential reuse
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """
    Main handler for transferring JSON files from S3 to PostgreSQL.

    Parameters:
    - event: The event triggering the lambda function.
    - context: The context of the lambda function.
    """
    logging.info("Starting Lambda handler")
    conn = None  # Initialize connection outside of the try block

    # Retrieve environment variables for S3 bucket names
    textract_bucket = os.environ['S3_BUCKET_NAME_TEXTRACT_JSON_RESPONSE']

    # Establish a connection to the PostgreSQL RDS instance
    try:
        conn = psycopg2.connect(
            dbname=os.environ['DB_NAME'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            host=os.environ['DB_HOST'],
            port=os.environ['DB_PORT']
        )
        logging.info("Database connection established.")
    except psycopg2.Error as db_err:
        logging.error(f"Failed to connect to database: {db_err}")
        return  # Stop execution if database connection fails

    try:
        # Move JSON files from Folder-A to Folder-B in S3
        move_json_files_to_destination_folder(textract_bucket, 'invoices/Folder-A/', 'invoices/Folder-B/')

        # Process and load JSON files from Folder-B into PostgreSQL in batches
        process_and_load_json_files_in_batches(conn, textract_bucket)

        # Call the stored procedure to update the final tables
        call_stored_procedure(conn)

    except Exception as proc_err:
        logging.error(f"An error occurred during processing: {proc_err}")
    finally:
        if conn:
            conn.close()
            logging.info("Database connection closed.")

def move_json_files_to_destination_folder(bucket_name, source_folder, destination_folder):
    """
    Moves JSON files from a source folder to a destination folder in the S3 bucket.

    Parameters:
    - bucket_name: The name of the S3 bucket.
    - source_folder: The source folder from which JSON files will be moved.
    - destination_folder: The destination folder to which JSON files will be moved.
    """
    logging.info(f"Moving JSON files from {source_folder} to {destination_folder} in S3 bucket.")
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=source_folder)
        if 'Contents' in response:
            for item in response['Contents']:
                key = item['Key']
                new_key = key.replace(source_folder, destination_folder)
                s3_client.copy_object(CopySource={'Bucket': bucket_name, 'Key': key},
                                      Bucket=bucket_name, Key=new_key)
                logging.info(f"Copied JSON file: {key} to {new_key}")

                # Delete the source JSON file only if the copy operation was successful
                s3_client.delete_object(Bucket=bucket_name, Key=key)
                logging.info(f"Deleted source JSON file: {key}")
        else:
            logging.info(f"No JSON files found in {source_folder}.")
    except Exception as e:
        logging.error(f"Error moving JSON files from {source_folder} to {destination_folder}: {e}")

def process_and_load_json_files_in_batches(conn, bucket_name, batch_size=10):
    """
    Processes and loads JSON files from Folder-B into PostgreSQL in batches.

    Parameters:
    - conn: The connection to the PostgreSQL database.
    - bucket_name: The name of the S3 bucket.
    - batch_size: The size of batches for processing JSON files.
    """
    logging.info(f"Processing and loading JSON files from Folder-B into PostgreSQL in batches of {batch_size}.")
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix='invoices/Folder-B/')
        if 'Contents' in response:
            batch = []  # Initialize an empty batch
            for item in response['Contents']:
                key = item['Key']
                try:
                    obj = s3_client.get_object(Bucket=bucket_name, Key=key)
                    json_data = json.loads(obj['Body'].read())
                    json_data_str = json.dumps(json_data)  # Serialize JSON data to string
                    batch.append((key, json_data_str))  # Add the key and serialized JSON data to the batch

                    # If the batch size reaches the specified limit, insert the batch into PostgreSQL
                    if len(batch) == batch_size:
                        insert_batch_to_postgres(conn, batch)
                        logging.info(f"Batch of {batch_size} JSON files loaded to PostgreSQL.")
                        batch = []  # Clear the batch after insertion
                except Exception as e:
                    logging.error(f"Error processing JSON file {key}: {e}")
            
            # Insert any remaining files in the last batch
            if batch:
                insert_batch_to_postgres(conn, batch)
                logging.info(f"Final batch of {len(batch)} JSON files loaded to PostgreSQL.")

            # Move JSON files from Folder-B to Folder-C
            move_json_files_to_destination_folder(bucket_name, 'invoices/Folder-B/', 'invoices/Folder-C/')
        else:
            logging.info("No JSON files found in Folder-B.")
    except Exception as e:
        logging.error(f"Error processing and loading JSON files from Folder-B: {e}")

def insert_batch_to_postgres(conn, batch):
    """
    Inserts a batch of JSON files into the PostgreSQL table.

    Parameters:
    - conn: The connection to the PostgreSQL database.
    - batch: The batch of JSON files to be inserted into the database.
    """
    try:
        with conn.cursor() as cursor:
            # Assume your table and columns are set up to take JSON data directly.
            # This may need adjustment based on the actual database schema.
            insert_query = """
            INSERT INTO public.in_invoice_processing (s3_object_key, textract_json)
            VALUES (%s, %s::jsonb)
            ON CONFLICT (s3_object_key) DO NOTHING
            """
            logging.info(f"Preparing to insert batch of {len(batch)} JSON files into PostgreSQL.")

            cursor.executemany(insert_query, batch)
            conn.commit()
            logging.info(f"Inserted batch of {len(batch)} JSON files into PostgreSQL.")
    except psycopg2.Error as e:
        logging.error(f"Failed to insert batch of JSON files: {e}")
        conn.rollback()  # Rollback the transaction in case of error


def call_stored_procedure(conn):
    """
    Calls the stored procedure to insert data into the final tables.

    Parameters:
    - conn: The connection to the PostgreSQL database.
    """
    try:
        with conn.cursor() as cursor:
            logging.info("Calling stored procedure: insert_vendor_invoice_product_line_item_data")
            cursor.execute("CALL insert_vendor_invoice_product_line_item_data();")
            conn.commit()
            logging.info("Stored procedure executed successfully.")
    except psycopg2.Error as e:
        logging.error(f"Failed to execute stored procedure: {e}")
        conn.rollback()  # Rollback the transaction in case of error