-- Step 2: Insert data into the line_item table from pro_line_item view
-- Ensure each line item record has the PK associated with the invoice table
INSERT INTO out_line_item (
    in_invoice_processing_id,
    s3_object_key,
    upload_date,
    invoice_id,
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
    expense_row
)
SELECT
    p.in_invoice_processing_id,
    p.s3_object_key,
    p.upload_date,
    i.invoice_id, -- Foreign key to the out_invoice table
    p.invoice_receipt_id,
    p.expense_document_index,
    p.line_item_index,
    p.product_code,
    p.brand,
    p.item_description,
    p.unit_price,
    p.net_amount,
    p.taxes,
    p.discount,
    p.quantity,
    p.price,
    p.unit_of_measure,
    p.pack,
    p.size,
    p.unit,
    p.weight,
    p.expense_row
FROM 
    pro_line_item p
JOIN 
    out_invoice i
ON 
    p.invoice_receipt_id = i.invoice_number; -- Assuming invoice_number in out_invoice matches invoice_receipt_id in pro_line_item