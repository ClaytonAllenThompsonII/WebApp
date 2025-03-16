-- Create a view to extract and normalize invoice data from JSONB columns
CREATE OR REPLACE VIEW ext1_invoice AS

SELECT
    -- Extract and rename fields from the in_invoice_processing table
    inp.id AS in_invoice_processing_id,          -- ID of the invoice processing record
    inp.s3_object_key,                          -- S3 key for locating the invoice document
    inp.received_timestamp,                     -- Timestamp when the invoice was received

    -- Extract indices and JSONB data from the ExpenseDocuments array
    ed.idx AS expense_document_index,           -- Index of the expense document in the JSON array
    sf.idx AS summary_field_index,              -- Index of the summary field in the JSON array
    sf.value ->> 'Type' AS summary_type,        -- Type of the summary field (raw JSON value)
    (sf.value -> 'Type' ->> 'Text') AS summary_type_text,  -- Type text of the summary field (text value)

    REPLACE(sf.value -> 'ValueDetection' ->> 'Text', E'\n', ' ') AS summary_value_text, -- Replace newlines with spaces
    (sf.value -> 'ValueDetection' ->> 'Confidence') AS summary_value_confidence, -- Confidence score of the value detection
    REPLACE(sf.value -> 'LabelDetection' ->> 'Text', E'\n', ' ') AS summary_label_text, -- Replace newlines with spaces
    (sf.value -> 'LabelDetection' ->> 'Confidence') AS summary_label_confidence, -- Confidence score of the label detection
    
    -- Handle group properties and types
    COALESCE(gp.value ->> 'Id', 'No Group Properties') AS group_property_id,    -- Group property ID
    COALESCE(types.type, 'No Types Available') AS type,                         -- Type of the group property

    -- Determine group type based on the Types array
    COALESCE(
    CASE
        WHEN 'RECEIVER' = ANY (SELECT jsonb_array_elements_text(gp.value -> 'Types')) THEN 'receiver'
        WHEN 'RECEIVER_SOLD_TO' = ANY (SELECT jsonb_array_elements_text(gp.value -> 'Types')) THEN 'sold_to'
        WHEN 'RECEIVER_SHIP_TO' = ANY (SELECT jsonb_array_elements_text(gp.value -> 'Types')) THEN 'ship_to'
		WHEN 'RECEIVER_BILL_TO' = ANY (SELECT jsonb_array_elements_text(gp.value -> 'Types')) THEN 'bill_to'
        WHEN 'VENDOR_REMIT_TO' = ANY (SELECT jsonb_array_elements_text(gp.value -> 'Types')) THEN 'remit_to'
        WHEN 'VENDOR' = ANY (SELECT jsonb_array_elements_text(gp.value -> 'Types')) THEN 'vendor'
        -- Add other cases as necessary for BILL_TO, SUPPLIER, etc.
    END, 
    'unclassified'  -- Defautl Value for records with empty group sets
    ) AS group_type

-- Specify the source table and perform lateral joins to extract JSONB array elements
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