CREATE OR REPLACE VIEW ext1_vendor AS


SELECT
  inp.id AS processing_id,
  inp.s3_object_key,
  (sf->'Type')::jsonb->>'Text' AS type_text,  -- Cast to JSONB before extraction
  sf->>'Type' AS type,

  (gp->'Types')::jsonb->>0 as group_text,
  gp->>'Types' AS group_type,

  (sf->'ValueDetection')::jsonb->>'Text' AS vd_text,  -- Cast to JSONB before extraction
  sf->>'ValueDetection' AS value_detection,

  (sf->'LabelDetection')::jsonb->>'Text' AS ld_text,  -- Cast to JSONB before extraction
  sf->>'LabelDetection' AS label_detection,

CASE
    WHEN (gp->'Types')::jsonb->>0 = 'VENDOR' THEN TRUE
    ELSE FALSE
END AS is_vendor,

CASE
    WHEN (gp->'Types')::jsonb->>0 = 'VENDOR_REMIT_TO'  THEN TRUE
    ELSE FALSE
END AS is_vendor_remit_to

FROM in_invoice_processing inp,
  LATERAL jsonb_array_elements(inp.textract_json->'ExpenseDocuments'->0->'SummaryFields') AS sf,
  LATERAL jsonb_array_elements(sf->'GroupProperties') AS gp;
