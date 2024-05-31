CREATE OR REPLACE VIEW for_invoice AS

SELECT
    -- Identifiers and Metadata
    in_invoice_processing_id,
    s3_object_key,
    received_timestamp,

    -- Invoice Details
    invoice_receipt_id,
    COALESCE(customer_number, account_number) AS customer_account_number,
    taxpayer_id,
    INITCAP(vendor_name) AS vendor_name,
    -- Assuming vendor_id will be populated later
    NULL::INT AS vendor_id,

    -- Dates: Removing day names and parsing to DATE
    TO_DATE(REGEXP_REPLACE(due_date, '^[A-Za-z]+, ', ''), 'MM/DD/YYYY') AS due_date,
    COALESCE(
        TO_DATE(REGEXP_REPLACE(invoice_receipt_date, '^[A-Za-z]+, ', ''), 'MM/DD/YYYY'),
        TO_DATE(REGEXP_REPLACE(delivery_date, '^[A-Za-z]+, ', ''), 'MM/DD/YYYY')
    ) AS invoice_receipt_date_plus,

    -- Purchase Order Number
    po_number,

    -- Payment Terms
    INITCAP(COALESCE(payment_terms_colon, terms, terms_upper)) AS payment_terms,

    -- Financial Data: Remove non-numeric characters and cast to DECIMAL
    REGEXP_REPLACE(COALESCE(invoice_total, Total, invoice_total_2, pay_this_amount, due_amount), '[^\d.-]', '', 'g')::DECIMAL AS total,
    REGEXP_REPLACE(total_gross_amount, '[^\d.-]', '', 'g')::DECIMAL AS subtotal,
    REGEXP_REPLACE(tax, '[^\d.-]', '', 'g')::DECIMAL AS tax,
    REGEXP_REPLACE(service_charge, '[^\d.-]', '', 'g')::DECIMAL AS service_charge,
    REGEXP_REPLACE(discount, '[^\d.-]', '', 'g')::DECIMAL AS discount

FROM
    ext2_invoice;