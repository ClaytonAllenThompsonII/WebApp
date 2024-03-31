CREATE OR REPLACE VIEW ext1_invoice AS
SELECT
    inp.id,
    inp.s3_object_key,
    jsonb_array_elements(inp.textract_json->'ExpenseDocuments')->'SummaryFields' AS summary,
    inp.received_timestamp
FROM
    in_invoice_processing inp;