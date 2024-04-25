CREATE OR REPLACE VIEW ext1_line_item AS
SELECT 
    inp.id AS in_invoice_processing_id,
    inp.s3_object_key,
    inp.received_timestamp,
    li.idx AS line_item_index,  -- New field added to represent line item index
    (li_expense_fields.value -> 'Type'::text) ->> 'Text'::text AS type_text,
    (li_expense_fields.value -> 'ValueDetection'::text) ->> 'Text'::text AS vd_text,
    REPLACE((li_expense_fields.value -> 'LabelDetection' ->> 'Text'), E'\n', ' | ') AS ld_text,
    sf.invoice_receipt_id AS invoice_receipt_id
    
FROM 
    in_invoice_processing inp,
    LATERAL jsonb_array_elements(((inp.textract_json -> 'ExpenseDocuments') -> 0) -> 'LineItemGroups') lig(value),
    LATERAL jsonb_array_elements(lig.value -> 'LineItems') WITH ORDINALITY AS li(value, idx),
    LATERAL jsonb_array_elements(li.value -> 'LineItemExpenseFields') li_expense_fields(value),
    LATERAL (
        SELECT 
            MAX(CASE WHEN summary_field -> 'Type' ->> 'Text' = 'INVOICE_RECEIPT_ID' THEN summary_field -> 'ValueDetection' ->> 'Text' END) AS invoice_receipt_id
        FROM 
            jsonb_array_elements((inp.textract_json -> 'ExpenseDocuments') -> 0 -> 'SummaryFields') AS summary_field
    ) sf

    
ORDER BY inp.id, li.idx;

COMMENT ON VIEW ext1_line_item IS $$
This view 'ext1_line_item' is designed to extract and transform detailed line item data from processed invoice documents. Each invoice is parsed using AWS Textract, which outputs JSON formatted text. The view performs the following operations:

1. **Extraction of Basic Invoice Data**: It retrieves the invoice processing ID, S3 object key, and timestamp from the 'in_invoice_processing' table, ensuring each entry is uniquely identifiable.

2. **Line Item Decomposition**: Utilizes LATERAL joins to navigate through nested JSON structures from Textract outputs. It breaks down 'LineItemGroups' into individual 'LineItems' and extracts associated 'LineItemExpenseFields'.

3. **Field Extraction**:
   - 'type_text': Extracts the type of each line item field (e.g., PRODUCT, PRICE).
   - 'vd_text': Retrieves the detected value of the field, such as quantities or amounts.
   - 'ld_text': Captures the label detection text, providing additional context for each value.

4. **Invoice Receipt ID Retrieval**: Aggregates and captures the invoice receipt ID from the 'SummaryFields' section of the Textract output. This ID is crucial for correlating line items back to specific invoices.

5. **Ordering**: The results are ordered by invoice processing ID and line item index to facilitate easy review and further processing.

This view is foundational for downstream data processing tasks, including detailed analytics and reporting on invoiced items, helping to understand expenditures, product categories, and other critical business metrics.
$$;