CREATE OR REPLACE VIEW ext1_invoice AS

SELECT
    inp.id AS in_invoice_processing_id,
    inp.s3_object_key,
    inp.received_timestamp,
    ed.idx AS expense_document_index,
    sf.idx AS summary_field_index,
    sf.value ->> 'Type' AS summary_type,
    (sf.value -> 'Type' ->> 'Text') AS summary_type_text,
    REPLACE(sf.value -> 'ValueDetection' ->> 'Text', E'\n', ' ') AS summary_value_text, -- Replace newlines with spaces
    (sf.value -> 'ValueDetection' ->> 'Confidence') AS summary_value_confidence,
    REPLACE(sf.value -> 'LabelDetection' ->> 'Text', E'\n', ' ') AS summary_label_text, -- Replace newlines with spaces
    (sf.value -> 'LabelDetection' ->> 'Confidence') AS summary_label_confidence,
    COALESCE(gp.value ->> 'Id', 'No Group Properties') AS group_property_id,
    COALESCE(types.type, 'No Types Available') AS type,
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
    ) AS group_type
FROM
    in_invoice_processing inp
JOIN LATERAL
     jsonb_array_elements(inp.textract_json -> 'ExpenseDocuments') WITH ORDINALITY AS ed(value, idx) ON true
JOIN LATERAL
    jsonb_array_elements(ed.value -> 'SummaryFields') WITH ORDINALITY AS sf(value, idx) ON true
LEFT JOIN LATERAL
    jsonb_array_elements(sf.value -> 'GroupProperties') AS gp(value) ON true
LEFT JOIN LATERAL
    jsonb_array_elements_text(COALESCE(gp.value -> 'Types', '["No Types Available"]'::jsonb)) AS types(type) ON true
ORDER BY
    inp.id, ed.idx, sf.idx;