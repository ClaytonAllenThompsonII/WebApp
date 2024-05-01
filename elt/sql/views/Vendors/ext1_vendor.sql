CREATE OR REPLACE VIEW ext1_vendor AS


SELECT
    inp.id AS processing_id,
    inp.s3_object_key,
    sf.idx AS field_index,
    sf.value ->> 'Type' AS field_type,
    (sf.value -> 'Type' ->> 'Text') AS type_text,
    (sf.value -> 'ValueDetection' ->> 'Text') AS value_text,
    (sf.value -> 'LabelDetection' ->> 'Text') AS label_text,
    COALESCE(gp.value ->> 'Types', '[]') AS group_types,
    sf.value -> 'ValueDetection' ->> 'Text' AS address_text,
  COALESCE(
    CASE
        WHEN 'RECEIVER_SOLD_TO' = ANY (SELECT jsonb_array_elements_text(gp.value -> 'Types')) THEN 'sold_to'
        WHEN 'RECEIVER_SHIP_TO' = ANY (SELECT jsonb_array_elements_text(gp.value -> 'Types')) THEN 'ship_to'
		WHEN 'RECEIVER_BILL_TO' = ANY (SELECT jsonb_array_elements_text(gp.value -> 'Types')) THEN 'bill_to'
        WHEN 'VENDOR_REMIT_TO' = ANY (SELECT jsonb_array_elements_text(gp.value -> 'Types')) THEN 'remit_to'
        WHEN 'VENDOR' = ANY (SELECT jsonb_array_elements_text(gp.value -> 'Types')) THEN 'vendor'
        -- Add other cases as necessary for BILL_TO, SUPPLIER, etc.
    END, 
    'unclassified'  -- Defautl Value for records with empty group sets
    ) AS address_role
FROM
    in_invoice_processing inp
JOIN LATERAL
    jsonb_array_elements(inp.textract_json -> 'ExpenseDocuments' -> 0 -> 'SummaryFields') WITH ORDINALITY AS sf(value, idx) ON TRUE
LEFT JOIN LATERAL
    jsonb_array_elements(sf.value -> 'GroupProperties') AS gp(value) ON TRUE

