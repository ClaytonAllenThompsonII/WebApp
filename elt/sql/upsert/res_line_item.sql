-- Step 2: Insert data into the out_line_item table
INSERT INTO out_line_item (
    in_invoice_processing_id,
    s3_object_key,
    upload_date,
    invoice_id,
    invoice_receipt_id,
    expense_document_index,
    line_item_index,
    product_id, -- Now includes product_id
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
    expense_row
)
SELECT
    pli.in_invoice_processing_id,
    pli.s3_object_key,
    pli.upload_date,
    i.invoice_id,
    pli.invoice_receipt_id,
    pli.expense_document_index,
    pli.line_item_index,
    p.product_id, -- Now includes product_id
    pli.product_code,
    pli.brand,
    pli.item_description,
    pli.unit_price,
    pli.net_amount,
    pli.taxes,
    pli.discount,
    pli.quantity,
    pli.price,
    pli.unit_of_measure,
    pli.pack,
    pli.size,
    pli.unit,
    pli.weight,
    pli.expense_row
FROM 
    pro_line_item_with_product_id pli
JOIN 
    out_invoice i
ON 
    pli.invoice_receipt_id = i.invoice_number
JOIN 
    out_product p
ON 
    pli.product_code = p.product_code
AND 
    pli.item_description = p.item_description
ON CONFLICT (line_item_id) DO UPDATE SET
    product_code = EXCLUDED.product_code,
    brand = EXCLUDED.brand,
    item_description = EXCLUDED.item_description,
    unit_price = EXCLUDED.unit_price,
    net_amount = EXCLUDED.net_amount,
    taxes = EXCLUDED.taxes,
    discount = EXCLUDED.discount,
    quantity = EXCLUDED.quantity,
    price = EXCLUDED.price,
    unit_of_measure = EXCLUDED.unit_of_measure,
    pack = EXCLUDED.pack,
    size = EXCLUDED.size,
    unit = EXCLUDED.unit,
    weight = EXCLUDED.weight,
    expense_row = EXCLUDED.expense_row,
    product_id = EXCLUDED.product_id;