CREATE OR REPLACE VIEW ext1_line_item AS
SELECT 
    inp.id AS in_invoice_processing_id,
    inp.s3_object_key,
    inp.received_timestamp,
    ed.idx AS expense_document_index,
    li.idx AS line_item_index,
    (li_expense_fields.value -> 'Type'::text) ->> 'Text'::text AS type_text,
    REPLACE((li_expense_fields.value -> 'ValueDetection'::text) ->> 'Text'::text, E'\n', ' ') AS vd_text,  -- Replace newlines with spaces
    REPLACE((li_expense_fields.value -> 'LabelDetection' ->> 'Text'::text), E'\n', ' ') AS ld_text,  -- Replace newlines with spaces
    sf.invoice_receipt_id AS invoice_receipt_id
FROM 
    in_invoice_processing inp
JOIN LATERAL
    jsonb_array_elements(inp.textract_json -> 'ExpenseDocuments') WITH ORDINALITY AS ed(value, idx) ON true
JOIN LATERAL
    jsonb_array_elements(ed.value -> 'LineItemGroups') lig(value) ON true
JOIN LATERAL
    jsonb_array_elements(lig.value -> 'LineItems') WITH ORDINALITY AS li(value, idx) ON true
JOIN LATERAL
    jsonb_array_elements(li.value -> 'LineItemExpenseFields') li_expense_fields(value) ON true
JOIN LATERAL (
        SELECT 
            MAX(CASE WHEN summary_field -> 'Type' ->> 'Text' = 'INVOICE_RECEIPT_ID' THEN summary_field -> 'ValueDetection' ->> 'Text' END) AS invoice_receipt_id
        FROM 
            jsonb_array_elements(ed.value -> 'SummaryFields') AS summary_field
    ) sf ON true
ORDER BY inp.id, ed.idx, li.idx;

COMMENT ON VIEW ext1_line_item IS $$
This view 'ext1_line_item' is designed to extract and transform detailed line item data from processed invoice documents. Each invoice is parsed using AWS Textract, which outputs JSON formatted text. The view performs the following operations:

1. **Extraction of Basic Invoice Data**: It retrieves the invoice processing ID, S3 object key, and timestamp from the 'in_invoice_processing' table, ensuring each entry is uniquely identifiable.

2. **Line Item Decomposition**: Utilizes LATERAL joins to navigate through nested JSON structures from Textract outputs. It breaks down 'LineItemGroups' into individual 'LineItems' and extracts associated 'LineItemExpenseFields'.