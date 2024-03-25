CREATE OR REPLACE VIEW view_vendor_details AS

SELECT
  inp.id AS processing_id,
  inp.s3_object_key,
  MAX(CASE WHEN sf.value->'Type'->>'Text' = 'NAME' THEN sf.value->'ValueDetection'->>'Text' END) AS vendor_name,
  MAX(CASE WHEN sf.value->'Type'->>'Text' = 'ADDRESS_BLOCK' THEN sf.value->'ValueDetection'->>'Text' END) AS vendor_address,
  MAX(CASE WHEN sf.value->'Type'->>'Text' = 'CITY' THEN sf.value->'ValueDetection'->>'Text' END) AS city,
  MAX(CASE WHEN sf.value->'Type'->>'Text' = 'STATE' THEN sf.value->'ValueDetection'->>'Text' END) AS state,
  MAX(CASE WHEN sf.value->'Type'->>'Text' = 'ZIP_CODE' THEN sf.value->'ValueDetection'->>'Text' END) AS zip_code,
  MAX(CASE WHEN sf.value->'Type'->>'Text' = 'VENDOR_URL' THEN sf.value->'ValueDetection'->>'Text' END) AS vendor_url,
  MAX(CASE WHEN sf.value->'Type'->>'Text' = 'VENDOR_PHONE' THEN sf.value->'ValueDetection'->>'Text' END) AS vendor_phone,
  MAX(CASE WHEN sf.value->'Type'->>'Text' = 'ACCOUNT_NUMBER' THEN sf.value->'ValueDetection'->>'Text' END) AS account_number

FROM
  in_invoice_processing inp,
  LATERAL jsonb_array_elements(inp.textract_json->'ExpenseDocuments'->0->'SummaryFields') AS sf
GROUP BY
  inp.id, inp.s3_object_key;






