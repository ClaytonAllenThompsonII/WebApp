import os
import psycopg2
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

def sync_data():
    """ 
    Fetch records from OLAP (RDS source) and insert them into the application database (local).
    """
    # Retrieve the last sync time
    last_sync_time = get_last_sync_time()

    # Database connection settings for RDS
    rds_host = os.getenv("RDS_INSTANCE_ENDPOINT")
    rds_dbname = os.getenv("RDS_DB_NAME")
    rds_user = os.getenv("RDS_DB_USER")
    rds_password = os.getenv("RDS_DB_PASSWORD")

    # Database connection settings for Local Database
    local_host = os.getenv("DB_HOST")
    local_dbname = os.getenv("DB_NAME")
    local_user = os.getenv("DB_USER")
    local_password = os.getenv("DB_PASSWORD")

    # Connect to RDS PostgreSQL
    rds_conn = psycopg2.connect(
        host=rds_host,
        dbname=rds_dbname,
        user=rds_user,
        password=rds_password
    )

    # Connect to Local PostgreSQL
    local_conn = psycopg2.connect(
        host=local_host,
        dbname=local_dbname,
        user=local_user,
        password=local_password
    )

    try:
        rds_cursor = rds_conn.cursor()
        local_cursor = local_conn.cursor()

        # Fetch new records from the OLAP database (RDS source)
        rds_cursor.execute("SELECT * FROM for_invoice WHERE batched_at IS NULL")
        invoices = rds_cursor.fetchall()

        # Insert new records into the application database (local)
        for invoice in invoices:
            local_cursor.execute("""
            INSERT INTO invoice (in_invoice_processing_id, s3_object_key, upload_date, account_number, 
                                 vendor_name, due_date, delivery_date, invoice_receipt_date, invoice_number, total, vendor_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NULL)
            """, invoice)
            
            # Update the batched_at timestamp in the OLAP database
            rds_cursor.execute("UPDATE for_invoice SET batched_at = %s WHERE in_invoice_processing_id = %s", 
                               (datetime.now(), invoice[0]))

        # Repeat the same process for line_item, vendor, and product domains
        for domain in ['line_item', 'vendor', 'product']:
            rds_cursor.execute(f"SELECT * FROM for_{domain} WHERE batched_at IS NULL")
            records = rds_cursor.fetchall()
            
            for record in records:
                local_cursor.execute(f"""
                INSERT INTO {domain} (/* Columns specific to {domain} */)
                VALUES (%s, %s, %s, /* other columns */)
                """, record)
                
                # Update the batched_at timestamp in the OLAP database
                rds_cursor.execute(f"UPDATE for_{domain} SET batched_at = %s WHERE id = %s", 
                                   (datetime.now(), record[0]))

        # Commit changes to both databases
        local_conn.commit()
        rds_conn.commit()

    finally:
        rds_cursor.close()
        local_cursor.close()
        rds_conn.close()
        local_conn.close()
        print("Data transfer completed successfully!")

def get_last_sync_time():
    # Implement retrieval of the last sync time from your preferred storage
    return datetime.min  # Placeholder, replace with actual retrieval logic

def update_last_sync_time(time):
    # Implement updating of the last sync time to your preferred storage
    pass

if __name__ == "__main__":
    sync_data()