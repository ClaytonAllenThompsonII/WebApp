CREATE OR REPLACE VIEW pro_line_item AS

WITH ranked_line_items AS (
    SELECT 
        *,
        ROW_NUMBER() OVER (
            PARTITION BY in_invoice_processing_id, expense_document_index, line_item_index 
            ORDER BY upload_date DESC
        ) AS rn
    FROM 
        for_line_item
)
SELECT
    in_invoice_processing_id,
    s3_object_key,
    upload_date,
    invoice_receipt_id,
    expense_document_index,
    
    line_item_index,
    product_code,
    brand,
    item_description,
    unit_price,
    net_amount,
    taxes,
    discount,
    quantity,
    price,
    unit_of_measure,
    pack,
    size,
    unit,
    weight,
    expense_row,
    quantity_size, 
    quantity_size2
FROM 
    ranked_line_items
WHERE 
    rn = 1
ORDER BY 
    in_invoice_processing_id, expense_document_index, line_item_index;