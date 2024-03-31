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
    Main handler for simply transferring JSON files from S3 to PostgreSQL.
    """
    logging.info("Starting Lambda handler")
    conn = None  # Initialize connection outside of the try block

    # Retrieve environment variables for S3 bucket name
    bucket_name = os.environ['S3_BUCKET_NAME_TEXTRACT_JSON_RESPONSE']

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
        # Simplified: Process and load all JSON files from S3 to PostgreSQL
        simple_process_and_load(conn, bucket_name)
    except Exception as proc_err:
        logging.error(f"An error occurred during processing: {proc_err}")
    finally:
        if conn:
            conn.close()
            logging.info("Database connection closed.")

def simple_process_and_load(conn, bucket_name):
    """
     This function reads JSON data from files stored in an S3 bucket and writes (loads)
    this data into a PostgreSQL database. It does not physically move the S3 files but processes their content. 
    """
    # Logging the start of the S3 bucket listing process
    logging.info("Listing objects in bucket: {}".format(bucket_name))
    try:
        response = s3_client.list_objects_v2(Bucket=bucket_name)
        logging.info("Objects listed in bucket: {}".format(bucket_name))

        if 'Contents' in response:
            for item in response['Contents']:
                key = item['Key']
                # Log the start of processing for each object
                logging.info("Processing object: {}".format(key))

                try:
                    # Log the start of fetching the object from S3
                    logging.info("Fetching object: {}".format(key))
                    obj = s3_client.get_object(Bucket=bucket_name, Key=key)
                    logging.info("Object fetched: {}".format(key))

                    # Decode the JSON data from the object
                    json_data = json.loads(obj['Body'].read())
                    logging.info("JSON data processed for key: {}".format(key))
                
                    # Here, directly load each JSON file's content to PostgreSQL
                    load_json_to_postgres(conn, key, json_data)
                    logging.info("JSON data loaded to PostgreSQL for key: {}".format(key))
                except Exception as e:
                    logging.error(f"Error processing objects from bucket {bucket_name}: {e}")
        else:
            logging.info("No objects found in bucket: {}".format(bucket_name))
    except Exception as e:
        logging.error(f"Error listing objects in bucket {bucket_name}: {e}")

def load_json_to_postgres(conn, key, json_data):
    """
    Loads a single JSON object's content into the PostgreSQL table.
    """
    try:
        with conn.cursor() as cursor:
            # Assume your table and columns are set up to take JSON data directly.
            # This may need adjustment based on the actual database schema.
            insert_query = """
            INSERT INTO public.in_invoice_processing (s3_object_key, textract_json) VALUES (%s, %s::jsonb)
            """
            logging.info(f"Preparing to insert JSON from {key} into PostgreSQL.")

            cursor.execute(insert_query, (key, json.dumps(json_data)))
            conn.commit()
            logging.info(f"Inserted JSON from {key} into PostgreSQL.")
    except psycopg2.Error as e:
        logging.error(f"Failed to insert JSON from {key}: {e}")
