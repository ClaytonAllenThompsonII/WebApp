CREATE TABLE out_invoice_processed (
  invoice_id INT PRIMARY KEY,                 -- Invoice ID as primary key
  in_invoice_processing_id INT,                -- Foreign key to track the source of the invoice
  s3_object_key VARCHAR(255),                  -- Key to locate the invoice document in S3
  upload_date TIMESTAMP,                       -- Timestamp when the invoice was uploaded
  account_number VARCHAR(255),                 -- Account number for the invoice
  vendor_name VARCHAR(255),                    -- Vendor name
  vendor_short_name VARCHAR(255),                          -- Vendor's short name
  due_date DATE,                               -- Date by which the payment for the invoice is due
  delivery_date DATE,                          -- Date on which the goods or services were delivered
  invoice_receipt_date DATE,                   -- Date when the invoice was issued/received
  invoice_number VARCHAR(255) UNIQUE,          -- Vendor assigned invoice number
  total DECIMAL,                               -- Total amount of the invoice including taxes and fees
  vendor_id INT,                               -- Foreign key linking to the vendor table
  inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Timestamp when the record is inserted into this table
  batched_at TIMESTAMP                        -- Timestamp when the record is batched into the application database
  -- FOREIGN KEY (vendor_id) REFERENCES out_vendor(vendor_id) ON DELETE SET NULL  -- Ensures integrity of reference to vendor table
);




-- Local testing using pgAdmin
psql -h localhost -U your_username -d your_database -c 
\copy out_invoice_processed(invoice_id, in_invoice_processing_id, s3_object_key, upload_date, account_number, vendor_name, vendor_short_name, due_date, delivery_date, invoice_receipt_date, invoice_number, total, vendor_id, inserted_at, batched_at) FROM '/Users/claytonthompson/Desktop/out_invoice.csv' DELIMITER ',' CSV HEADER NULL AS 'NULL';


-c \
\copy out_invoice_processed(invoice_id, in_invoice_processing_id, s3_object_key, upload_date, account_number, vendor_name, vendor_short_name, due_date, delivery_date, invoice_receipt_date, invoice_number, total, vendor_id, inserted_at, batched_at) FROM '/Users/claytonthompson/Desktop/out_invoice.csv' DELIMITER ',' CSV HEADER NULL AS 'NULL';