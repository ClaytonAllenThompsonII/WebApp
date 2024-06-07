-- Create a view to consolidate and format vendor data from ext1_vendor
CREATE OR REPLACE VIEW for_vendor AS

SELECT
    in_invoice_processing_id,
    s3_object_key,
    received_timestamp AS upload_date,

    -- Vendor Account Number
    COALESCE(account_number_label, account_number_hash, customer_number_label, customer_number_customer) AS account_number,

    -- Vendor Name
    COALESCE(name_vendor, INITCAP(vendor_name)) AS vendor_name,

    -- Vendor Phone (format to XXX-XXX-XXXX)
    CASE
        WHEN LENGTH(REGEXP_REPLACE(COALESCE(vendor_phone, vendor_phone_sales, vendor_phone_person, vendor_phone_null), '[^\d]', '', 'g')) = 10 THEN
            SUBSTRING(REGEXP_REPLACE(COALESCE(vendor_phone, vendor_phone_sales, vendor_phone_person, vendor_phone_null), '[^\d]', '', 'g') FROM 1 FOR 3) || '-' ||
            SUBSTRING(REGEXP_REPLACE(COALESCE(vendor_phone, vendor_phone_sales, vendor_phone_person, vendor_phone_null), '[^\d]', '', 'g') FROM 4 FOR 3) || '-' ||
            SUBSTRING(REGEXP_REPLACE(COALESCE(vendor_phone, vendor_phone_sales, vendor_phone_person, vendor_phone_null), '[^\d]', '', 'g') FROM 7)
        ELSE NULL
    END AS vendor_phone,

       -- Vendor Address Fields
    INITCAP(COALESCE(vendor_address_block,vendor_address, vendor_address_null, remit_to_address, vendor_address_remit_to)) AS vendor_address,
    INITCAP(COALESCE(vendor_street, remit_to_street)) AS vendor_street,
    INITCAP(REGEXP_REPLACE(COALESCE(vendor_city, remit_to_city), ',', '')) AS vendor_city,
    UPPER(LEFT(REGEXP_REPLACE(COALESCE(vendor_state, remit_to_state), '[^\w]', ''), 2)) AS vendor_state,
    REGEXP_REPLACE(COALESCE(vendor_zip_code, remit_to_zip_code), ',', '') AS vendor_zip_code,
    INITCAP(COALESCE(vendor_address_block, remit_to_address_block)) AS address_block, 

    INITCAP(COALESCE(remit_to_address, vendor_address_remit_to, vendor_address_remit_to_colon, vendor_address_remit_to_plain)) AS vendor_remit_address,

    -- Remit To Address
    INITCAP(remit_to_street) AS remit_to_street,
    INITCAP(REGEXP_REPLACE(remit_to_city, ',', '')) AS remit_to_city,
    UPPER(LEFT(REGEXP_REPLACE(remit_to_state, '[^\w]', ''), 2)) AS remit_to_state,
    remit_to_zip_code,
    INITCAP(remit_to_address_block) as remit_to_address_block

FROM
    ext2_vendor
ORDER BY
    in_invoice_processing_id;