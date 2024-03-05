CREATE OR REPLACE VIEW ext1_line_item AS
SELECT
    inp.id AS in_invoice_processing_id,
    inp.s3_object_key,
    li_expense_fields.value AS line_item_expense_field,
    inp.received_timestamp
FROM
    in_invoice_processing inp,
    jsonb_array_elements(inp.textract_json->'ExpenseDocuments'->0->'LineItemGroups') AS lig(value),
    jsonb_array_elements(lig.value->'LineItems') AS li(value),
    jsonb_array_elements(li.value->'LineItemExpenseFields') AS li_expense_fields(value);
