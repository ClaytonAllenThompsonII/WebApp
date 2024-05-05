CREATE OR REPLACE VIEW ext2_vendor_address_clean AS

WITH AddressDetails AS (
    SELECT
        processing_id,
        s3_object_key,
        INITCAP(TRIM(REGEXP_REPLACE(value_text, '[,.]+', '', 'g'))) AS value_text,
        type_text,
        address_role
    FROM
        ext1_vendor
    WHERE
        type_text IN ('STREET', 'CITY', 'STATE', 'ZIP_CODE', 'ADDRESS_BLOCK')
),
PivotedAddresses AS (
    SELECT
        processing_id,
        s3_object_key,
        MAX(CASE WHEN type_text = 'STREET' THEN value_text END) AS street,
        MAX(CASE WHEN type_text = 'CITY' THEN value_text END) AS city,
        UPPER(MAX(CASE WHEN type_text = 'STATE' THEN value_text END)) AS state,
        MAX(CASE WHEN type_text = 'ZIP_CODE' THEN value_text END) AS zip_code,
        MAX(CASE WHEN type_text = 'ADDRESS_BLOCK' THEN value_text END) AS address_block,
        address_role
    FROM
        AddressDetails
    GROUP BY
        processing_id, s3_object_key, address_role
),
FinalAddresses AS (
    SELECT
        processing_id,
        s3_object_key,
        MAX(CASE WHEN address_role = 'remit_to' THEN street END) AS remit_street,
        MAX(CASE WHEN address_role = 'remit_to' THEN city END) AS remit_city,
        MAX(CASE WHEN address_role = 'remit_to' THEN state END) AS remit_state,
        MAX(CASE WHEN address_role = 'remit_to' THEN zip_code END) AS remit_zip_code,
        MAX(CASE WHEN address_role = 'remit_to' THEN address_block END) AS remit_address_block,
        MAX(CASE WHEN address_role = 'sold_to' THEN street END) AS sold_street,
        MAX(CASE WHEN address_role = 'sold_to' THEN city END) AS sold_city,
        MAX(CASE WHEN address_role = 'sold_to' THEN state END) AS sold_state,
        MAX(CASE WHEN address_role = 'sold_to' THEN zip_code END) AS sold_zip_code,
        MAX(CASE WHEN address_role = 'sold_to' THEN address_block END) AS sold_address_block,
        -- Add more roles as needed
        MAX(CASE WHEN address_role = 'ship_to' THEN street END) AS ship_street,
        MAX(CASE WHEN address_role = 'ship_to' THEN city END) AS ship_city,
        MAX(CASE WHEN address_role = 'ship_to' THEN state END) AS ship_state,
        MAX(CASE WHEN address_role = 'ship_to' THEN zip_code END) AS ship_zip_code,
        MAX(CASE WHEN address_role = 'ship_to' THEN address_block END) AS ship_address_block
    FROM
        PivotedAddresses
    GROUP BY
        processing_id, s3_object_key
)
SELECT *
FROM FinalAddresses
ORDER BY processing_id, s3_object_key;