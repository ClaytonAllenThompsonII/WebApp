CREATE OR REPLACE VIEW ext1_line_item AS
SELECT
    inp.id AS in_invoice_processing_id,
    inp.s3_object_key,
    
    inp.received_timestamp,

    (li_expense_fields->'Type')::jsonb->>'Text' AS type_text,  -- Cast to JSONB before extraction
    li_expense_fields->>'Type' AS type,

    (li_expense_fields->'ValueDetection')::jsonb->>'Text' AS vd_text,  -- Cast to JSONB before extraction
    li_expense_fields->>'ValueDetection' AS value_detection,

    (li_expense_fields->'LabelDetection')::jsonb->>'Text' AS ld_text,  -- Cast to JSONB before extraction
    li_expense_fields->>'LabelDetection' AS label_detection,

    li_expense_fields.value AS line_item_expense_field
FROM
    in_invoice_processing inp,
    jsonb_array_elements(inp.textract_json->'ExpenseDocuments'->0->'LineItemGroups') AS lig(value),
    jsonb_array_elements(lig.value->'LineItems') AS li(value),
    jsonb_array_elements(li.value->'LineItemExpenseFields') AS li_expense_fields(value);

    -- where (li_expense_fields->'Type')::jsonb->>'Text' = 'ITEM'
    -- for All ITEMs (line item product descriptions)
