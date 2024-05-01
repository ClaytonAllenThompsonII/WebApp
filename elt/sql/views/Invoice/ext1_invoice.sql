CREATE OR REPLACE VIEW ext1_invoice AS

SELECT
    inp.id AS in_invoice_processing_id,
    inp.s3_object_key,
    inp.received_timestamp,
    sf.idx AS summary_field_index,
    sf.value ->> 'Type' AS summary_type,
    (sf.value -> 'Type' ->> 'Text') AS summary_type_text,
    (sf.value -> 'ValueDetection' ->> 'Text') AS summary_value_text,
    (sf.value -> 'ValueDetection' ->> 'Confidence') AS summary_value_confidence,
    (sf.value -> 'LabelDetection' ->> 'Text') AS summary_label_text,
    (sf.value -> 'LabelDetection' ->> 'Confidence') AS summary_label_confidence,
    COALESCE(gp.value ->> 'Id', 'No Group Properties') AS group_property_id,
    COALESCE(types.type, 'No Types Available') AS type
FROM
    in_invoice_processing inp
JOIN LATERAL
    jsonb_array_elements(inp.textract_json -> 'ExpenseDocuments' -> 0 -> 'SummaryFields') WITH ORDINALITY AS sf(value, idx) ON true
LEFT JOIN LATERAL
    jsonb_array_elements(sf.value -> 'GroupProperties') AS gp(value) ON true
LEFT JOIN LATERAL
    jsonb_array_elements_text(COALESCE(gp.value -> 'Types', '["No Types Available"]'::jsonb)) AS types(type) ON true
ORDER BY
    inp.id, sf.idx;