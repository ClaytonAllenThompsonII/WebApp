CREATE OR REPLACE VIEW for_vendor AS
SELECT
    processing_id,
    s3_object_key,
    INITCAP(vendor_name) AS vendor_name, -- Capitalizes each word in the vendor name
    INITCAP(vendor_address) AS vendor_address, -- Capitalizes each word in the address
    INITCAP(street) AS street,
    INITCAP(city) AS city,
    state,
    country,
    zip_code,
    REGEXP_REPLACE(vendor_phone, '[^\d]+', '', 'g') AS vendor_phone, -- Removes non-numeric characters
    LOWER(vendor_url) AS vendor_url -- Converts URL to lowercase
FROM
    ext1_vendor;
