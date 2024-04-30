CREATE OR REPLACE VIEW ext2_vendor AS

WITH vendor_details AS (
    SELECT
        inp.id AS processing_id,
        inp.s3_object_key,
        MAX(CASE WHEN sf.value -> 'Type' ->> 'Text' = 'ACCOUNT_NUMBER' THEN sf.value -> 'ValueDetection' ->> 'Text' END) AS account_number,
        MAX(CASE WHEN sf.value -> 'Type' ->> 'Text' = 'VENDOR_PHONE' THEN sf.value -> 'ValueDetection' ->> 'Text' END) AS vendor_phone,
        MAX(CASE WHEN sf.value -> 'Type' ->> 'Text' = 'VENDOR_URL' THEN sf.value -> 'ValueDetection' ->> 'Text' END) AS vendor_url,
        MAX(CASE WHEN sf.value -> 'Type' ->> 'Text' = 'VENDOR_NAME' OR (sf.value -> 'Type' ->> 'Text' = 'NAME' AND ev.is_vendor) THEN sf.value -> 'ValueDetection' ->> 'Text' END) AS vendor_name,
        MAX(CASE WHEN sf.value -> 'Type' ->> 'Text' = 'STREET' AND ev.is_vendor THEN sf.value -> 'ValueDetection' ->> 'Text' END) AS street,
        MAX(CASE WHEN sf.value -> 'Type' ->> 'Text' = 'CITY' AND ev.is_vendor THEN sf.value -> 'ValueDetection' ->> 'Text' END) AS city,
        MAX(CASE WHEN sf.value -> 'Type' ->> 'Text' = 'STATE' AND ev.is_vendor THEN sf.value -> 'ValueDetection' ->> 'Text' END) AS state,
        MAX(CASE WHEN sf.value -> 'Type' ->> 'Text' = 'ZIP_CODE' AND ev.is_vendor THEN sf.value -> 'ValueDetection' ->> 'Text' END) AS zip_code,
        MAX(CASE WHEN sf.value -> 'Type' ->> 'Text' = 'REMIT_ADDRESS' OR (sf.value -> 'Type' ->> 'Text' = 'ADDRESS_BLOCK' AND ev.is_vendor_remit_to) THEN sf.value -> 'ValueDetection' ->> 'Text' END) AS remit_address_block
    FROM
        in_invoice_processing inp
    JOIN
        LATERAL jsonb_array_elements(inp.textract_json -> 'ExpenseDocuments' -> 0 -> 'SummaryFields') AS sf(value) ON TRUE
    JOIN
        ext1_vendor ev ON ev.processing_id = inp.id AND ev.s3_object_key = inp.s3_object_key
    GROUP BY
        inp.id, inp.s3_object_key
)
SELECT
    vd.processing_id,
    vd.s3_object_key,
    vd.account_number,
    vd.vendor_phone,
    vd.vendor_url,
    vd.vendor_name,
    vd.street,
    vd.city,
    vd.state,
    vd.zip_code,
    vd.remit_address_block
FROM
    vendor_details vd;