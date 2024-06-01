CREATE OR REPLACE VIEW for_line_item AS

SELECT
    -- Extract necessary fields
    received_timestamp,
    s3_object_key,
    in_invoice_processing_id,
    invoice_receipt_id,
    expense_document_index,
    line_item_index,
    
    -- Normalize item description
    COALESCE(item, item_description, item_null, item_item, item_item_description) AS item_description,
    -- Normalize Brand
    COALESCE(item_brand, other_brand) as brand, 

    -- Unit: Case
    COALESCE()

    -- Unit Price (pre-discount)
    COALESCE(unit_price, unit_pricing, unit_price_ea, unit_price_upper, unit_price_mixed) as list_unit_price,

    -- Unit Discount ($ amount)
    COALESCE(other_unit_disc, other_discount, other_disc_rate) as discount,

    -- Unit Net Amount
    COALESCE()


    -- Taxes (for line item)
    -- Total (for line item)





    
    -- Normalize Unit of Measure (UOM)
    COALESCE(other_unit_net, other_unit_tax_amount, other_unit_net_amount, other_unit_disc, other_unit_net) AS uom,
    
    -- Normalize quantity
    COALESCE(quantity, q quantity_btl_qty, quantity_full_cases, quantity_btls_ord_dlv, quantity_qpc, quantity_description, quantity_cs_ord_dlv, quantity_case_qty, quantity_pack, quantity_null) AS quantity,
    
    -- Normalize unit price
    COALESCE(unit_price, unit_pricing, unit_price_ea, unit_price_upper, unit_price_mixed, unit_net_amount, unit_gross, unit_price_null) AS unit_price,
    
    -- Normalize total price
    COALESCE(price, price_amount, price_net_amount, price_total, price_extended, price_null) AS total_price

FROM
    ext2_line_item
ORDER BY
    in_invoice_processing_id, expense_document_index, line_item_index;