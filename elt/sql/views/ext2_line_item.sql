CREATE OR REPLACE VIEW ext2_line_item AS
SELECT
    in_invoice_processing_id,
    s3_object_key,
    MAX(CASE WHEN line_item_expense_field->'Type'->>'Text' = 'PRODUCT_CODE' THEN line_item_expense_field->'ValueDetection'->>'Text' END) AS product_code,
    MAX(CASE WHEN line_item_expense_field->'Type'->>'Text' = 'ITEM' THEN line_item_expense_field->'LabelDetection'->>'Text' END) AS item_description,
    MAX(CASE WHEN line_item_expense_field->'Type'->>'Text' = 'QUANTITY' THEN line_item_expense_field->'ValueDetection'->>'Text' END) AS quantity,
    MAX(CASE WHEN line_item_expense_field->'Type'->>'Text' = 'UNIT_PRICE' THEN line_item_expense_field->'ValueDetection'->>'Text' END) AS unit_price,
    MAX(CASE WHEN line_item_expense_field->'Type'->>'Text' = 'PRICE' THEN line_item_expense_field->'ValueDetection'->>'Text' END) AS total_price,
    received_timestamp
FROM
    ext1_line_item
GROUP BY
    in_invoice_processing_id,
    s3_object_key,
    received_timestamp;
