CREATE OR REPLACE VIEW ext2_line_item AS


SELECT
    inp.id AS in_invoice_processing_id,
    inp.s3_object_key,
    li_expense_fields.value AS line_item_expense_field,
    inp.received_timestamp,
    MAX(CASE WHEN ((li_expense_fields->'Type')::jsonb->>'Text') = 'PRODUCT_CODE' THEN (li_expense_fields->'ValueDetection')::jsonb->>'Text' END) AS product_code,
    MAX(CASE WHEN ((li_expense_fields->'Type')::jsonb->>'Text') = 'ITEM' THEN (li_expense_fields->'ValueDetection')::jsonb->>'Text' END) AS item,
    MAX(CASE WHEN ((li_expense_fields->'Type')::jsonb->>'Text') = 'QUANTITY' THEN (li_expense_fields->'ValueDetection')::jsonb->>'Text' END) AS quantity,
    MAX(CASE WHEN ((li_expense_fields->'Type')::jsonb->>'Text') = 'UNIT_PRICE' THEN (li_expense_fields->'ValueDetection')::jsonb->>'Text' END) AS unit_price,
    MAX(CASE WHEN ((li_expense_fields->'Type')::jsonb->>'Text') = 'PRICE' THEN (li_expense_fields->'ValueDetection')::jsonb->>'Text' END) AS price
FROM
    in_invoice_processing inp,
    jsonb_array_elements(inp.textract_json->'ExpenseDocuments'->0->'LineItemGroups') AS lig(value),
    jsonb_array_elements(lig.value->'LineItems') AS li(value),
    jsonb_array_elements(li.value->'LineItemExpenseFields') AS li_expense_fields(value)
	
	group by in_invoice_processing_id, s3_object_key, li_expense_fields.value, li;


