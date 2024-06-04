INSERT INTO invoice (
  in_invoice_processing_id,  -- Unique ID for each invoice processing entry
  s3_object_key,             -- S3 object key for the invoice file
  upload_date,               -- Date when the invoice was uploaded
  account_number,            -- Account number associated with the invoice
  vendor_name,               -- Name of the vendor
  delivery_date,             -- Date of delivery, formatted as DATE
  invoice_receipt_date,      -- Date when the invoice was received, formatted as DATE
  due_date,                  -- Due date for payment, formatted as DATE
  invoice_number,            -- Cleaned and formatted invoice number
  total,                     -- Total amount of the invoice
  vendor_id                  -- Placeholder for vendor_id, to be assigned later
)
SELECT 
  in_invoice_processing_id,  -- Select unique ID for each invoice processing entry
  s3_object_key,             -- Select S3 object key for the invoice file
  upload_date,               -- Select date when the invoice was uploaded
  account_number,            -- Select account number associated with the invoice
  vendor_name,               -- Select name of the vendor
  delivery_date_date,        -- Select delivery date, using DATE type directly
  invoice_date_date,         -- Select invoice receipt date, using DATE type directly
  due_date_date,             -- Select due date for payment, using DATE type directly
  invoice_number,            -- Select cleaned and formatted invoice number
  total,                     -- Select total amount of the invoice
  NULL                       -- Placeholder for vendor_id, to be assigned later
FROM for_invoice;            -- Source view containing cleaned and formatted invoice data