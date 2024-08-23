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

       # Sync the invoice domain
        sync_domain(rds_cursor, local_cursor, 'invoice', """
            INSERT INTO out_invoice_processed (
                in_invoice_processing_id, s3_object_key, upload_date, account_number, 
                vendor_name, due_date, delivery_date, invoice_receipt_date, 
                invoice_number, total, vendor_id, inserted_at, batched_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (invoice_number) DO NOTHING
        """)

        # Sync the line item domain
        sync_domain(rds_cursor, local_cursor, 'line_item', """
            INSERT INTO out_line_item_processed (
                line_item_id, in_invoice_processing_id, s3_object_key, upload_date, invoice_id, 
                invoice_receipt_id, expense_document_index, line_item_index, product_id, 
                product_code, brand, item_description, unit_price, net_amount, 
                taxes, discount, quantity, price, unit_of_measure, pack, size, 
                unit, weight, expense_row, gl3_id, gl3_name
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (line_item_id) DO NOTHING
        """)

        # Sync the product domain
        sync_domain(rds_cursor, local_cursor, 'product_enhanced', """
            INSERT INTO out_product_enhanced (
                product_code, item_description, brand, last_updated, 
                generated_product_name, enhanced_details, estimated_expiration
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (product_code, item_description) DO NOTHING
        """)

        # Commit changes to both databases
        local_conn.commit()
        rds_conn.commit()

    finally:
        rds_cursor.close()
        local_cursor.close()
        rds_conn.close()
        local_conn.close()
        print("Data transfer completed successfully!")

def sync_domain(rds_cursor, local_cursor, domain, insert_query):
    """
    Sync a specific domain from the OLAP database to the local application database.

    Parameters:
    - rds_cursor: Cursor for the RDS connection.
    - local_cursor: Cursor for the local database connection.
    - domain: The domain to sync (invoice, line_item, product, etc.).
    - insert_query: The SQL query to insert records into the local database.
    """
    table_name = f"for_{domain}"
    
    # Fetch new records from the OLAP database (RDS source)
    rds_cursor.execute(f"SELECT * FROM {table_name} WHERE batched_at IS NULL")
    records = rds_cursor.fetchall()

    # Insert new records into the application database (local)
    for record in records:
        local_cursor.execute(insert_query, record)
        
        # Update the batched_at timestamp in the OLAP database
        rds_cursor.execute(f"UPDATE {table_name} SET batched_at = %s WHERE id = %s", 
                           (datetime.now(), record[0]))

if __name__ == "__main__":
    sync_data()