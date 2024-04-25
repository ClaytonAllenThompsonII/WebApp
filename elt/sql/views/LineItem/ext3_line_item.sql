SELECT 
    in_invoice_processing_id,
    s3_object_key,
    received_timestamp,
    line_item_index,
    COALESCE(product_code, 'N/A') AS product_code,
    COALESCE(item, 'No item description available') AS item,
    COALESCE(unit_price, '0.00') AS unit_price,
    COALESCE(NULLIF((other_details ->> 'UNIT | DISC'), ''), '0.00') AS unit_disc,
    COALESCE(NULLIF((other_details ->> 'TAXES'), ''), '0.00') AS taxes,
    COALESCE(NULLIF((other_details ->> 'UNIT | NET | AMOUNT'), ''), '0.00') AS unit_net_amount,
    COALESCE(price, '0.00') AS price,
    COALESCE(NULLIF((other_details ->> 'CS | ORD/DLV'), ''), 'Not specified') AS cs_ord_dlv,
    COALESCE(NULLIF((other_details ->> 'BTLS | ORD/DLV'), ''), 'Not specified') AS btls_ord_dlv,
    COALESCE(expense_row, 'No details') AS expense_row,
    COALESCE(NULLIF((other_details ->> 'Unknown Label'), ''), 'None') AS unknown_label
FROM 
    ext2_line_item;
