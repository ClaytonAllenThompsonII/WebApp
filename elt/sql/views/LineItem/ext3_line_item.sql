-- This SQL view joins line item data from `ext2_line_item` with unit of measure (UOM) data from `ext1_uom`.
-- It formats data comprehensively, handling missing values with defaults and ensures each line item is fully described.

CREATE OR REPLACE VIEW ext3_line_item AS

SELECT 
    l.in_invoice_processing_id,
    l.s3_object_key,
    l.received_timestamp,
    l.line_item_index,
    l.invoice_receipt_id,
    COALESCE(l.product_code, 'N/A') AS product_code,
    INITCAP(COALESCE(REGEXP_REPLACE(l.item, E'[\\n\\r]+', ' ', 'g'), 'No item description available')) AS item,
    INITCAP(COALESCE(
        CASE 
            WHEN POSITION('Item#:' IN l.item) > 0 
            THEN SUBSTRING(l.item, 1, POSITION('Item#:' IN l.item) - 1)
            ELSE l.item
        END, 
        'No item description available'
    )) AS item_short,
    INITCAP(COALESCE(NULLIF(l.other_details ->> 'Brand', ''), 'No Brand Specified')) AS Brand,
    COALESCE(CAST(NULLIF(REGEXP_REPLACE(l.price, '[^0-9.]', '', 'g'), '') AS NUMERIC), 0.00) AS price, 
	COALESCE(CAST(NULLIF(REGEXP_REPLACE(l.unit_price, '[-,]', '.', 'g'), '') AS NUMERIC), 0.00) AS unit_price,   -- Unit price of the item, '0.00' if not available
	COALESCE(CAST(NULLIF(REGEXP_REPLACE(SUBSTRING(l.quantity FROM '^\d+'), '[^\d.]', '', 'g'), '') AS NUMERIC), 0) AS quantity, -- Extracted and cleaned numeric quantity

	CAST(NULLIF(REGEXP_REPLACE(SPLIT_PART(COALESCE(NULLIF(l.other_details ->> 'CS | ORD/DLV', ''), 'Not specified'), '/', 1), '[^0-9.]', '', 'g'), '') AS NUMERIC) AS cases_ordered,
	CAST(NULLIF(REGEXP_REPLACE(SPLIT_PART(COALESCE(NULLIF(l.other_details ->> 'CS | ORD/DLV', ''), 'Not specified'), '/', 2), '[^0-9.]', '', 'g'), '') AS NUMERIC) AS cases_delivered,

    COALESCE(NULLIF((l.other_details ->> 'CS | ORD/DLV'), ''), 'Not specified') AS cs_ord_dlv,  -- Cases ordered/delivered
    COALESCE(NULLIF((l.other_details ->> 'BTLS | ORD/DLV'), ''), 'Not specified') AS btls_ord_dlv, -- Bottles ordered/delivere
	COALESCE(CAST(NULLIF(REGEXP_REPLACE(SUBSTRING(l.other_details ->> 'CsPK' FROM '[0-9]+[.,]*[0-9]*'), '[-,]', '.', 'g'), '') AS NUMERIC), 0) AS CsPK,
	COALESCE(CAST(NULLIF(REGEXP_REPLACE(SUBSTRING(l.other_details ->> 'PK-Size' FROM '[0-9]+[.,]*[0-9]*'), '[-,]', '.', 'g'), '') AS NUMERIC), 0) AS PK_Size,
	COALESCE(CAST(NULLIF(REGEXP_REPLACE(SUBSTRING(l.other_details ->> 'Qpc' FROM '[0-9]+[.,]*[0-9]*'), '[-,]', '.', 'g'), '') AS NUMERIC), 0) AS Qpc,
	COALESCE(CAST(NULLIF(REGEXP_REPLACE(SUBSTRING(l.other_details ->> 'Case Qty' FROM '[0-9]+[.,]*[0-9]*'), '[-,]', '.', 'g'), '') AS NUMERIC), 0) AS Case_Qty,
	COALESCE(u.BPC, 'Not relevant') AS uom_BPC,  -- Boxes per case
    COALESCE(CAST(NULLIF(REGEXP_REPLACE(u.BPC, '[^\d.]', '', 'g'), '') AS NUMERIC), 0.00) AS uom_bpc_numeric,
    COALESCE(u.Size, 'Not relevant') AS uom_Size,  -- Size of the item
    COALESCE(CAST(NULLIF(REGEXP_REPLACE(u.Size, '[^\d.]', '', 'g'), '') AS NUMERIC), 0.00) AS uom_size_numeric,
	COALESCE(u.product_number, 'Not relevant') AS uom_product_number, -- UOM product number
    COALESCE(u.Note, 'Not relevant') AS uom_Note, -- Additional notes
    COALESCE(REGEXP_REPLACE(l.expense_row,E'[\\n\\r]+', ' ', 'g'), 'No details') AS expense_row,  -- Details about the expense row
    COALESCE(CAST(NULLIF(REGEXP_REPLACE(SUBSTRING(l.other_details ->> 'Ln' FROM '[0-9]+[.,]*[0-9]*'), '[-,]', '.', 'g'), '') AS NUMERIC), 0) AS Page_Line,
    COALESCE(NULLIF((l.other_details ->> 'Unknown Label'), ''), 'None') AS unknown_label  -- Handles any unknown labels
    -- Other fields and transformations...
FROM 
    ext2_line_item l
LEFT JOIN 
    ext1_uom u ON l.product_code = u.product_number AND l.s3_object_key = u.s3_object_key AND l.in_invoice_processing_id = u.invoice_id
ORDER BY 
    l.in_invoice_processing_id, l.line_item_index;  
