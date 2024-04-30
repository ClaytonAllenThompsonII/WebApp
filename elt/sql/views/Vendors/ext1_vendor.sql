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
    CASE
        WHEN 'VENDOR' = ANY(ARRAY(SELECT jsonb_array_elements_text(COALESCE(gp.value -> 'Types', '[]'::jsonb)))) THEN TRUE
        ELSE FALSE
    END AS is_vendor,
    CASE
        WHEN 'VENDOR_REMIT_TO' = ANY(ARRAY(SELECT jsonb_array_elements_text(COALESCE(gp.value -> 'Types', '[]'::jsonb)))) THEN TRUE
        ELSE FALSE
    END AS is_vendor_remit_to
FROM
    in_invoice_processing inp
JOIN LATERAL
    jsonb_array_elements(inp.textract_json -> 'ExpenseDocuments' -> 0 -> 'SummaryFields') WITH ORDINALITY AS sf(value, idx) ON true
LEFT JOIN LATERAL
    jsonb_array_elements(sf.value -> 'GroupProperties') AS gp(value) ON true;

