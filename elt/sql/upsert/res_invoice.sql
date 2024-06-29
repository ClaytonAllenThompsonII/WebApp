-- Insert new records or update existing ones in the invoice table
INSERT INTO out_invoice (
  in_invoice_processing_id,  -- Foreign key to track the source of the invoice
  s3_object_key,             -- Key to locate the invoice document in S3
  upload_date,               -- Timestamp when the invoice was uploaded
  account_number,            -- Account number for the invoice
  vendor_name,               -- Vendor name
  delivery_date,             -- Date on which the goods or services were delivered
  invoice_receipt_date,      -- Date when the invoice was issued/received
  due_date,                  -- Date by which the payment for the invoice is due
  invoice_number,            -- Vendor assigned invoice number
  total,                     -- Total amount of the invoice including taxes and fees
  vendor_id,                 -- Foreign key linking to the vendor table
  inserted_at,               -- Timestamp when the record is inserted into this table
  batched_at                 -- Timestamp when the record is batched into the application database (initially NULL)
)
-- Select data from the pro_invoice view, joining with out_vendor to get the vendor_id
SELECT 
  pi.in_invoice_processing_id,  -- Source of the invoice
  pi.s3_object_key,             -- S3 location key of the invoice document
  pi.upload_date,               -- Upload timestamp
  pi.account_number,            -- Invoice account number
  pi.vendor_name,               -- Vendor name (standardized)
  pi.delivery_date,             -- Delivery date (DATE type)
  pi.invoice_receipt_date,      -- Invoice receipt date (DATE type)
  pi.due_date,                  -- Due date (DATE type)
  pi.invoice_number,            -- Unique invoice number
  pi.total,                     -- Total amount of the invoice
  ov.vendor_id,                 -- Look up the vendor_id from the out_vendor table
  CURRENT_TIMESTAMP,            -- Set the inserted_at timestamp to the current time
  NULL                          -- Initially setting batched_at to NULL
FROM pro_invoice pi
LEFT JOIN out_vendor ov 
  ON pi.account_number = ov.account_number
  AND pi.vendor_name = ov.vendor_name
-- Handle conflicts based on the unique invoice_number
ON CONFLICT (invoice_number)
-- Update existing records with new values when a conflict is detected
DO UPDATE SET
  in_invoice_processing_id = EXCLUDED.in_invoice_processing_id,
  s3_object_key = EXCLUDED.s3_object_key,
  upload_date = EXCLUDED.upload_date,
  account_number = EXCLUDED.account_number,
  vendor_name = EXCLUDED.vendor_name,
  delivery_date = EXCLUDED.delivery_date,
  invoice_receipt_date = EXCLUDED.invoice_receipt_date,
  due_date = EXCLUDED.due_date,
  total = EXCLUDED.total,
  vendor_id = EXCLUDED.vendor_id,
  inserted_at = EXCLUDED.inserted_at;