-- This SQL view joins line item data from `ext2_line_item` with unit of measure (UOM) data from `ext1_uom`.
-- It ensures all line items have complete and formatted data, including handling missing values with defaults.
CREATE OR REPLACE VIEW ext3_line_item AS

SELECT 
    l.in_invoice_processing_id,   -- Unique ID of the invoice processing session
    l.s3_object_key,              -- Reference to the S3 object where the original document is stored
    l.received_timestamp,         -- Timestamp when the invoice data was received
    l.line_item_index,
    l.invoice_receipt_id,            -- Index of the line item within the invoice
    COALESCE(l.product_code, 'N/A') AS product_code,  -- Product code of the line item, 'N/A' if not available
    INITCAP(COALESCE(REGEXP_REPLACE(l.item, E'[\\n\\r]+', ' ', 'g'), 'No item description available')) AS item,  -- Item description, capitalized, with line breaks removed
    COALESCE(CAST(NULLIF(REGEXP_REPLACE(l.unit_price, '[-,]', '.', 'g'), '') AS NUMERIC), 0.00) AS unit_price,   -- Unit price of the item, '0.00' if not available
    COALESCE(NULLIF((l.other_details ->> 'UNIT | DISC'), ''), '0.00') AS unit_disc,  -- Unit discount, '0.00' if not applicable
    COALESCE(NULLIF((l.other_details ->> 'TAXES'), ''), '0.00') AS taxes,  -- Taxes applied, '0.00' if none
    COALESCE(NULLIF((l.other_details ->> 'UNIT | NET | AMOUNT'), ''), '0.00') AS unit_net_amount, -- Net amount after discounts
    COALESCE(CAST(NULLIF(REGEXP_REPLACE(REGEXP_REPLACE(l.price, '[^0-9.-]', '', 'g'), '[-,]', '.', 'g'), '') AS NUMERIC), 0.00) AS price,  -- Total price of the line item, '0.00' if not available
    COALESCE(NULLIF((l.other_details ->> 'CS | ORD/DLV'), ''), 'Not specified') AS cs_ord_dlv,  -- Cases ordered/delivered
    COALESCE(NULLIF((l.other_details ->> 'BTLS | ORD/DLV'), ''), 'Not specified') AS btls_ord_dlv, -- Bottles ordered/delivered
    -- UOM fields to enrich line item data with additional details like packaging and notes
    COALESCE(u.product_number, 'Not relevant') AS uom_product_number, -- UOM product number, default 'Not relevant'
    COALESCE(u.BPC, 'Not relevant') AS uom_BPC,  -- Boxes per case, default 'Not relevant'
    COALESCE(u.Size, 'Not relevant') AS uom_Size,  -- Size of the item, default 'Not relevant'
    COALESCE(u.Note, 'Not relevant') AS uom_Note, -- Additional notes, default 'Not relevant'
    COALESCE(REGEXP_REPLACE(l.expense_row,E'[\\n\\r]+', ' ', 'g'), 'No details') AS expense_row,  -- Details about the expense row, 'No details' if empty
    COALESCE(NULLIF((l.other_details ->> 'Unknown Label'), ''), 'None') AS unknown_label  -- Handles any unknown labels
FROM 
    ext2_line_item l  -- Source table containing line item details
LEFT JOIN 
    ext1_uom u  -- Joins with the UOM details to enrich line item data
ON 
    l.product_code = u.product_number AND  -- Matching on product code
    l.s3_object_key = u.s3_object_key AND  -- Ensuring S3 keys match for consistency
    l.in_invoice_processing_id = u.invoice_id  -- Linking on invoice ID for further verification
ORDER BY 
    l.in_invoice_processing_id, l.line_item_index; -- Ordering for easier readability and processing

-- This view is essential for reconciling and presenting detailed line item data with added UOM attributes.
-- Typically these UOM should be included in the Textract API payload under LineItemExpenses, but in some cases
-- These fields are tagged as OTHER and roll up under SummaryFields. 
-- Will need to keep an eye on slowly changing dimensions related to unit economics or line items. 
