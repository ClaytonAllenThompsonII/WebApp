CREATE OR REPLACE VIEW ext2_line_item AS


SELECT 
    in_invoice_processing_id,
    s3_object_key,
    received_timestamp,
    invoice_receipt_id,
    line_item_index,
    MAX(CASE WHEN type_text = 'PRODUCT_CODE' THEN vd_text ELSE NULL END) AS product_code,
    COALESCE(MAX(CASE WHEN type_text = 'ITEM' THEN vd_text ELSE NULL END), MAX(CASE WHEN type_text = 'EXPENSE_ROW' THEN vd_text ELSE NULL END)) AS item,
    MAX(CASE WHEN type_text = 'UNIT_PRICE' THEN vd_text ELSE NULL END) AS unit_price,
    MAX(CASE WHEN type_text = 'PRICE' THEN vd_text ELSE NULL END) AS price,
    jsonb_object_agg(COALESCE(ld_text, 'Unknown Label'), vd_text) FILTER (WHERE type_text = 'OTHER' AND vd_text IS NOT NULL) AS other_details,
    MAX(CASE WHEN type_text = 'EXPENSE_ROW' THEN vd_text ELSE NULL END) AS expense_row
FROM 
    ext1_line_item
GROUP BY
    in_invoice_processing_id, s3_object_key, invoice_receipt_id, received_timestamp, line_item_index
ORDER BY
    in_invoice_processing_id, line_item_index;


