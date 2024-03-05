CREATE OR REPLACE VIEW ext1_vendor AS
SELECT
    inp.id AS processing_id,
    inp.s3_object_key,
    MAX(CASE WHEN sf.value->>'VENDOR_NAME' THEN sf.value->'ValueDetection'->>'Text' END) AS vendor_name,
    MAX(CASE WHEN sf.value->>'Type' = 'ADDRESS' THEN sf.value->'ValueDetection'->>'Text' END) AS vendor_address,
    MAX(CASE WHEN sf.value->>'Type' = 'STREET' THEN sf.value->'ValueDetection'->>'Text' END) AS street,
    -- Add other fields as necessary, following the pattern above
    MAX(CASE WHEN sf.value->>'Type' = 'CITY' THEN sf.value->'ValueDetection'->>'Text' END) AS city,
    MAX(CASE WHEN sf.value->>'Type' = 'STATE' THEN sf.value->'ValueDetection'->>'Text' END) AS state,
    MAX(CASE WHEN sf.value->>'Type' = 'COUNTRY' THEN sf.value->'ValueDetection'->>'Text' END) AS country,
    MAX(CASE WHEN sf.value->>'Type' = 'ZIP_CODE' THEN sf.value->'ValueDetection'->>'Text' END) AS zip_code,
    MAX(CASE WHEN sf.value->>'Type' = 'VENDOR_PHONE' THEN sf.value->'ValueDetection'->>'Text' END) AS vendor_phone,
    MAX(CASE WHEN sf.value->>'Type' = 'VENDOR_URL' THEN sf.value->'ValueDetection'->>'Text' END) AS vendor_url
FROM
    in_invoice_processing inp,
    jsonb_array_elements(inp.textract_json->'ExpenseDocuments'->0->'SummaryFields') AS sf(value)
GROUP BY
    inp.id, inp.s3_object_key;
