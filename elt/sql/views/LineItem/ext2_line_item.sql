CREATE OR REPLACE VIEW ext2_line_item AS


SELECT 
    in_invoice_processing_id,
    s3_object_key,
    received_timestamp,
    invoice_receipt_id,
    expense_document_index,
    line_item_index,
    
    -- Extract product code
    MAX(CASE WHEN type_text = 'PRODUCT_CODE' THEN vd_text ELSE NULL END) AS product_code,
    
    -- Extract item description, prioritizing 'ITEM' over 'EXPENSE_ROW'
      COALESCE(
        MAX(CASE WHEN type_text = 'ITEM' THEN regexp_replace(vd_text, '(.*)(ITEM#:.*)', '\1') ELSE NULL END), 
        MAX(CASE WHEN type_text = 'EXPENSE_ROW' THEN regexp_replace(vd_text, '(.*)(ITEM#:.*)', '\1') ELSE NULL END)
    ) AS item,
    -- Extract specific fields under ITEM
    MAX(CASE WHEN type_text = 'ITEM' AND ld_text = 'Description' THEN vd_text ELSE NULL END) AS item_description,
    MAX(CASE WHEN type_text = 'ITEM' AND ld_text = 'ITEM' THEN regexp_replace(vd_text, '(.*)(ITEM#:.*)', '\1') ELSE NULL END) AS item_item,
    MAX(CASE WHEN type_text = 'ITEM' AND ld_text = 'ITEM DESCRIPTION' THEN vd_text ELSE NULL END) AS item_item_description,
    MAX(CASE WHEN type_text = 'ITEM' AND ld_text = 'Brand' THEN vd_text ELSE NULL END) AS item_brand,
    MAX(CASE WHEN type_text = 'ITEM' AND ld_text IS NULL THEN regexp_replace(vd_text, '(.*)(ITEM#:.*)', '\1') ELSE NULL END) AS item_null,
    MAX(CASE WHEN type_text = 'ITEM' AND ld_text = 'Category' THEN vd_text ELSE NULL END) AS item_category,

    -- Extract unit price
    MAX(CASE WHEN type_text = 'UNIT_PRICE' THEN vd_text ELSE NULL END) AS unit_price,
    -- Extract unit price variations
    MAX(CASE WHEN type_text = 'UNIT_PRICE' AND ld_text = 'Price' THEN vd_text ELSE NULL END) AS unit_pricing,
    MAX(CASE WHEN type_text = 'UNIT_PRICE' AND ld_text = 'Price Ea.' THEN vd_text ELSE NULL END) AS unit_price_ea,
    MAX(CASE WHEN type_text = 'UNIT_PRICE' AND ld_text = 'UNIT PRICE' THEN vd_text ELSE NULL END) AS unit_price_upper,
    MAX(CASE WHEN type_text = 'UNIT_PRICE' AND ld_text = 'Unit Price' THEN vd_text ELSE NULL END) AS unit_price_mixed,
    MAX(CASE WHEN type_text = 'UNIT_PRICE' AND ld_text = 'UNIT NET AMOUNT' THEN vd_text ELSE NULL END) AS unit_net_amount,
    MAX(CASE WHEN type_text = 'UNIT_PRICE' AND ld_text = 'Gross' THEN vd_text ELSE NULL END) AS unit_gross,
    MAX(CASE WHEN type_text = 'UNIT_PRICE' AND ld_text IS NULL THEN vd_text ELSE NULL END) AS unit_price_null,

    -- Extract total price
    MAX(CASE WHEN type_text = 'PRICE' THEN vd_text ELSE NULL END) AS price,
      -- Extract total price variations
    MAX(CASE WHEN type_text = 'PRICE' AND ld_text = 'Amount' THEN vd_text ELSE NULL END) AS price_amount,
    MAX(CASE WHEN type_text = 'PRICE' AND ld_text = 'Net Amount' THEN vd_text ELSE NULL END) AS price_net_amount,
    MAX(CASE WHEN type_text = 'PRICE' AND ld_text = 'TOTAL' THEN vd_text ELSE NULL END) AS price_total,
    MAX(CASE WHEN type_text = 'PRICE' AND ld_text = 'EXTENDED PRICE' THEN vd_text ELSE NULL END) AS price_extended,
    MAX(CASE WHEN type_text = 'PRICE' AND ld_text IS NULL THEN vd_text ELSE NULL END) AS price_null,

    
    -- Extract quantity
    MAX(CASE WHEN type_text = 'QUANTITY' THEN vd_text ELSE NULL END) as quantity,
    MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'Quantity' THEN vd_text ELSE NULL END) AS quantity2,
    -- Extract quantity variations
    MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'Cs/PK' THEN vd_text ELSE NULL END) AS quantity_cs_pk,
    MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'QTY' THEN vd_text ELSE NULL END) AS quantity_qty,
    MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'ITEM' THEN vd_text ELSE NULL END) AS quantity_item,
    MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'Btl Qty' THEN vd_text ELSE NULL END) AS quantity_btl_qty,
    MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'Full Cases' THEN vd_text ELSE NULL END) AS quantity_full_cases,
    MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'BTLS ORD/DLV' THEN vd_text ELSE NULL END) AS quantity_btls_ord_dlv,
    MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'Qpc' THEN vd_text ELSE NULL END) AS quantity_qpc,
    MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'Description' THEN vd_text ELSE NULL END) AS quantity_description,
    MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'CS ORD/DLV' THEN vd_text ELSE NULL END) AS quantity_cs_ord_dlv,
    MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'Case Qty' THEN vd_text ELSE NULL END) AS quantity_case_qty,
    MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'PACK' THEN vd_text ELSE NULL END) AS quantity_pack,
    MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text IS NULL THEN vd_text ELSE NULL END) AS quantity_null,
    
     -- Extract specific OTHER fields
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text IS NULL THEN vd_text ELSE NULL END) AS other_null,
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Ln' THEN vd_text ELSE NULL END) AS other_ln,

    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'PK-Size' THEN vd_text ELSE NULL END) AS other_pk_size,
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Brand' THEN vd_text ELSE NULL END) AS other_brand,
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Cs/PK' THEN vd_text ELSE NULL END) AS other_cs_pk,
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'TAXES' THEN vd_text ELSE NULL END) AS other_taxes,
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'UNIT DISC' THEN vd_text ELSE NULL END) AS other_unit_disc,
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Disc Rate' THEN vd_text ELSE NULL END) AS other_disc_rate,
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Btl Price' THEN vd_text ELSE NULL END) AS other_btl_price,
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Size' THEN vd_text ELSE NULL END) AS other_size,
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Unit Tax' THEN vd_text ELSE NULL END) AS other_unit_tax,
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Case Qty' THEN vd_text ELSE NULL END) AS other_case_qty,
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Btl Qty' THEN vd_text ELSE NULL END) AS other_btl_qty,
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'UNIT TAX AMOUNT' THEN vd_text ELSE NULL END) AS other_unit_tax_amount,
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'UNIT NET AMOUNT' THEN vd_text ELSE NULL END) AS other_unit_net_amount,
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'PACK' THEN vd_text ELSE NULL END) AS other_pack,
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'BTLS ORD/DLV' THEN vd_text ELSE NULL END) AS other_btls_ord_dlv,
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'CS ORD/DLV' THEN vd_text ELSE NULL END) AS other_cs_ord_dlv,

    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'SIZE' THEN vd_text ELSE NULL END) AS other_size_upper,
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'DOY' THEN vd_text ELSE NULL END) AS other_doy,
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Discount' THEN vd_text ELSE NULL END) AS other_discount,
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Gallons/Liters' THEN vd_text ELSE NULL END) AS other_gallons_liters,
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Tax' THEN vd_text ELSE NULL END) AS other_tax,
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Unit Net' THEN vd_text ELSE NULL END) AS other_unit_net,
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Bottles' THEN vd_text ELSE NULL END) AS other_bottles,
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Qpc' THEN vd_text ELSE NULL END) AS other_qpc,

    -- Aggregate other details into a JSONB object, ensuring keys are not null
    jsonb_object_agg(
        COALESCE(ld_text, 'Unknown Label'), 
        vd_text
    ) FILTER (WHERE type_text = 'OTHER' AND vd_text IS NOT NULL) AS other_details,
    
    -- Retain expense row information, if available
    MAX(CASE WHEN type_text = 'EXPENSE_ROW' THEN vd_text ELSE NULL END) AS expense_row

FROM 
    ext1_line_item
GROUP BY
    in_invoice_processing_id, s3_object_key, invoice_receipt_id, received_timestamp, expense_document_index, line_item_index
ORDER BY
    in_invoice_processing_id, expense_document_index, line_item_index;


