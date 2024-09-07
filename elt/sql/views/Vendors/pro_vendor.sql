CREATE OR REPLACE VIEW pro_vendor AS
WITH ranked_vendors AS (
    SELECT 
        in_invoice_processing_id,
        s3_object_key,
        upload_date,
        COALESCE(account_number, LAG(account_number) OVER (PARTITION BY vendor_short_name ORDER BY upload_date DESC)) AS account_number, 
        vendor_name,
        vendor_short_name,
        vendor_phone,
        vendor_address,
        vendor_street,
        vendor_city,
        vendor_state,
        vendor_zip_code,
        address_block,
        vendor_remit_address,
        remit_to_street,
        remit_to_city,
        remit_to_state,
        remit_to_zip_code,
        remit_to_address_block,
        ROW_NUMBER() OVER (
            PARTITION BY vendor_short_name 
            ORDER BY 
                CASE 
                    WHEN account_number IS NOT NULL THEN 1 
                    ELSE 2 
                END, 
                upload_date DESC
        ) AS rn
    FROM 
        for_vendor
)
SELECT 
    in_invoice_processing_id AS most_recent_in_invoice_processing_id,
    s3_object_key AS most_recent_s3_object_key,
    upload_date AS most_recent_upload_date,
    account_number,
    vendor_name,
    vendor_short_name,
    vendor_phone,
    vendor_address,
    vendor_street,
    vendor_city,
    vendor_state,
    vendor_zip_code,
    address_block,
    vendor_remit_address,
    remit_to_street,
    remit_to_city,
    remit_to_state,
    remit_to_zip_code,
    remit_to_address_block
FROM 
    ranked_vendors
WHERE 
    rn = 1  -- Select only the most recent record for each vendor
ORDER BY 
    vendor_short_name, 
    most_recent_upload_date DESC;