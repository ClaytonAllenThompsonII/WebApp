-- Create a view to select distinct vendors with the most recent records from for_vendor using CTEs and window functions
CREATE OR REPLACE VIEW pro_vendor AS
WITH ranked_vendors AS (
    -- Select all fields from for_vendor and assign row numbers based on vendor_name and vendor_phone
    -- Partition by vendor_name and vendor_phone to rank rows for each vendor, ordering by upload_date in descending order
    SELECT 
        *,
        ROW_NUMBER() OVER (PARTITION BY vendor_name, account_number ORDER BY upload_date DESC) AS rn
    FROM 
        for_vendor
)
-- Select fields from ranked_vendors where the row number is 1, ensuring the most recent record for each vendor
-- This approach helps consolidate vendor records that may have differing address fields into a single, most recent record
SELECT
    in_invoice_processing_id AS most_recent_in_invoice_processing_id,  -- The most recent in_invoice_processing_id
    s3_object_key AS most_recent_s3_object_key,                        -- The most recent S3 object key
    upload_date AS most_recent_upload_date,                            -- The most recent upload date
    account_number,                                                    -- Vendor's account number
    vendor_name,                                                       -- Vendor's name
    vendor_phone,                                                      -- Vendor's phone number
    vendor_address,                                                    -- Vendor's address
    vendor_street,                                                     -- Vendor's street address
    vendor_city,                                                       -- Vendor's city
    vendor_state,                                                      -- Vendor's state
    vendor_zip_code,                                                   -- Vendor's ZIP code
    address_block,                                                     -- Vendor's address block
    vendor_remit_address,                                              -- Vendor's remit-to address
    remit_to_street,                                                   -- Remit-to street address
    remit_to_city,                                                     -- Remit-to city
    remit_to_state,                                                    -- Remit-to state
    remit_to_zip_code,                                                 -- Remit-to ZIP code
    remit_to_address_block                                             -- Remit-to address block
FROM 
    ranked_vendors
WHERE 
    rn = 1  -- Select only the most recent record for each vendor
ORDER BY 
    vendor_name, 
    vendor_phone;  -- Order by vendor_name and vendor_phone for organized output