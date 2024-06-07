-- Create a view to format and clean line item data from ext2_line_item
CREATE OR REPLACE VIEW for_line_item AS
SELECT
    in_invoice_processing_id,
    s3_object_key,
    received_timestamp AS upload_date,
    invoice_receipt_id,
    expense_document_index,
    line_item_index,
    
    -- Product code
    product_code,
    COALESCE(INITCAP(item_brand), INITCAP(other_brand)) as brand, 
    -- Item description, removing any extraneous "ITEM#:" details
    COALESCE(INITCAP(item), regexp_replace(item_description, 'ITEM#:.*', '', 'g')) AS item_description,
    
    -- Unit price, converting to numeric and handling different formats
    CASE 
        WHEN unit_price IS NOT NULL THEN NULLIF(regexp_replace(regexp_replace(unit_price, '-', '.', 'g'), '[^\d.]', '', 'g'), '')::NUMERIC
        WHEN unit_pricing IS NOT NULL THEN NULLIF(regexp_replace(regexp_replace(unit_pricing, '-', '.', 'g'), '[^\d.]', '', 'g'), '')::NUMERIC
        WHEN unit_price_ea IS NOT NULL THEN NULLIF(regexp_replace(regexp_replace(unit_price_ea, '-', '.', 'g'), '[^\d.]', '', 'g'), '')::NUMERIC
        WHEN unit_price_upper IS NOT NULL THEN NULLIF(regexp_replace(regexp_replace(unit_price_upper, '-', '.', 'g'), '[^\d.]', '', 'g'), '')::NUMERIC
        WHEN unit_price_mixed IS NOT NULL THEN NULLIF(regexp_replace(regexp_replace(unit_price_mixed, '-', '.', 'g'), '[^\d.]', '', 'g'), '')::NUMERIC
        WHEN unit_net_amount IS NOT NULL THEN NULLIF(regexp_replace(regexp_replace(unit_net_amount, '-', '.', 'g'), '[^\d.]', '', 'g'), '')::NUMERIC
        WHEN unit_gross IS NOT NULL THEN NULLIF(regexp_replace(regexp_replace(unit_gross, '-', '.', 'g'), '[^\d.]', '', 'g'), '')::NUMERIC
        WHEN unit_price_null IS NOT NULL THEN NULLIF(regexp_replace(unit_price_null, '[^\d.]', '', 'g'), '')::NUMERIC

        ELSE NULL
    END AS unit_price,

    -- Total price, converting to numeric and handling different formats
    CASE 
        WHEN price IS NOT NULL THEN NULLIF(regexp_replace(regexp_replace(price, '-', '.', 'g'), '[^\d.]', '', 'g'), '')::NUMERIC
        WHEN price_amount IS NOT NULL THEN NULLIF(regexp_replace(regexp_replace(price_amount, '-', '.', 'g'), '[^\d.]', '', 'g'), '')::NUMERIC
        WHEN price_net_amount IS NOT NULL THEN NULLIF(regexp_replace(regexp_replace(price_net_amount, '-', '.', 'g'), '[^\d.]', '', 'g'), '')::NUMERIC
        WHEN price_total IS NOT NULL THEN NULLIF(regexp_replace(regexp_replace(price_total, '-', '.', 'g'), '[^\d.]', '', 'g'), '')::NUMERIC
        WHEN price_extended IS NOT NULL THEN NULLIF(regexp_replace(regexp_replace(price_extended, '-', '.', 'g'), '[^\d.]', '', 'g'), '')::NUMERIC
        WHEN price_null IS NOT NULL THEN NULLIF(regexp_replace(regexp_replace(price_null, '-', '.', 'g'), '[^\d.]', '', 'g'), '')::NUMERIC

        ELSE NULL
    END AS price


    
FROM 
    ext2_line_item
ORDER BY
    in_invoice_processing_id, expense_document_index, line_item_index;