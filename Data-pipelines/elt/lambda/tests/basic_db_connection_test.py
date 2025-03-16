import os
import logging
import psycopg2

# Configure detailed logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(module)s - %(funcName)s - %(pathname)s:%(lineno)d - %(message)s')

def lambda_handler(event, context):
    logging.info("Lambda handler started - Phase 2: Database Connection Test")
    
    # Retrieve database connection details from environment variables
    dbname = os.environ['DB_NAME']
    user = os.environ['DB_USER']
    password = os.environ['DB_PASSWORD']
    host = os.environ['DB_HOST']
    port = os.environ['DB_PORT']
    
    logging.info("Attempting to establish database connection...")
    
    try:
        # Establish a connection to the database
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
        logging.info("Database connection established successfully.")
        
        # Optionally, perform a simple query (e.g., SELECT 1) to validate the connection
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        
        logging.info("Simple database query executed successfully.")
    except Exception as e:
        logging.error(f"Failed to connect to database: {e}")
        return {'status': 'error', 'message': str(e)}
    
    return {'status': 'success', 'message': 'Database connection and simple query executed successfully.'}
