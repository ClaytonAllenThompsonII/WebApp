CREATE OR REPLACE VIEW pro_invoice AS

WITH ranked_invoices AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY invoice_number ORDER BY upload_date DESC) AS rn
    FROM 
        for_invoice
)
SELECT
    in_invoice_processing_id,
    s3_object_key,
    upload_date,
    account_number,
    vendor_name,
    vendor_short_name,
    delivery_date_date AS delivery_date, -- Cast to DATE type
    invoice_date_date AS invoice_receipt_date, -- Cast to DATE type
    due_date_date AS due_date, -- Cast to DATE type
    invoice_number,
    total,
    terms
FROM 
    ranked_invoices
WHERE 
    rn = 1
ORDER BY 
    invoice_date DESC;