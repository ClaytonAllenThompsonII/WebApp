CREATE OR REPLACE VIEW validation_missing_product_code AS

WITH ext1 AS (
  -- Reconstruct ext1_line_item to extract basic line item fields from the JSON.
  SELECT 
    inp.id AS in_invoice_processing_id,
    inp.s3_object_key,
    inp.received_timestamp,
    ed.idx AS expense_document_index,
    li.idx AS line_item_index,
    -- Extract type, value and label text while replacing newlines with spaces.
    (li_expense_fields.value -> 'Type') ->> 'Text' AS type_text,
    REPLACE((li_expense_fields.value -> 'ValueDetection') ->> 'Text', E'\n', ' ') AS vd_text,
    REPLACE((li_expense_fields.value -> 'LabelDetection') ->> 'Text', E'\n', ' ') AS ld_text
  FROM 
    in_invoice_processing inp
  JOIN LATERAL jsonb_array_elements(inp.textract_json -> 'ExpenseDocuments') WITH ORDINALITY AS ed(value, idx) ON true
  JOIN LATERAL jsonb_array_elements(ed.value -> 'LineItemGroups') AS lig(value) ON true
  JOIN LATERAL jsonb_array_elements(lig.value -> 'LineItems') WITH ORDINALITY AS li(value, idx) ON true
  JOIN LATERAL jsonb_array_elements(li.value -> 'LineItemExpenseFields') AS li_expense_fields(value) ON true
),
ext2 AS (
  -- Apply your extraction logic to compute product_code.
  SELECT 
    in_invoice_processing_id,
    s3_object_key,
    received_timestamp,
    expense_document_index,
    line_item_index,
    COALESCE(
      -- Primary: use PRODUCT_CODE if available and non-empty.
      NULLIF(MAX(CASE WHEN type_text = 'PRODUCT_CODE' THEN vd_text END), ''),
      
      -- Secondary: extract digits following "ITEM#:" from an EXPENSE_ROW field.
      CASE 
        WHEN MAX(CASE WHEN type_text = 'EXPENSE_ROW' THEN vd_text END) 
             ~* E'ITEM#:\\s*\\d+' 
        THEN regexp_replace(
                MAX(CASE WHEN type_text = 'EXPENSE_ROW' THEN vd_text END),
                E'.*ITEM#:\\s*(\\d+).*',
                E'\\1',
                'i'
             )
        ELSE NULL
      END,
      
      -- Tertiary: use the OTHER field when ld_text equals 'SARASO 21 Item ID'.
      NULLIF(MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'SARASO 21 Item ID' THEN vd_text END), '')
    ) AS product_code
  FROM ext1
  GROUP BY 
    in_invoice_processing_id, s3_object_key, received_timestamp, expense_document_index, line_item_index
)
-- Return only those line items where the extracted product_code is null.
SELECT *
FROM ext2
WHERE product_code IS NULL;