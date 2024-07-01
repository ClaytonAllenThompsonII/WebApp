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
    COALESCE(
        NULLIF(regexp_replace(unit_pricing, '-', '.', 'g'), '')::NUMERIC,
        NULLIF(regexp_replace(unit_price_ea, '-', '.', 'g'), '')::NUMERIC,
        NULLIF(regexp_replace(primary_unit_price_upper, '-', '.', 'g'), '')::NUMERIC,
        NULLIF(regexp_replace(unit_price_mixed, '-', '.', 'g'), '')::NUMERIC,
        NULLIF(regexp_replace(unit_price_null, '-', '.', 'g'), '')::NUMERIC

    ) AS unit_price,

    -- Net amount
    COALESCE(
        CASE WHEN (case_net_amount::TEXT ~ '^[0-9.-]+$') THEN case_net_amount ELSE NULL END::NUMERIC,
        CASE WHEN (bottle_net_amount::TEXT ~ '^[0-9.-]+$') THEN bottle_net_amount ELSE NULL END::NUMERIC,
        CASE WHEN (unit_net_amount::TEXT ~ '^[0-9.-]+$') THEN unit_net_amount ELSE NULL END::NUMERIC,
        CASE WHEN (price_extended::TEXT ~ '^[0-9.-]+$') THEN price_extended ELSE NULL END::NUMERIC,
        CASE WHEN (other_unit_net::TEXT ~ '^[0-9.-]+$') THEN other_unit_net ELSE NULL END::NUMERIC,
        CASE WHEN (other_null_unit_net_amount::TEXT ~ '^[0-9.-]+$') THEN other_null_unit_net_amount ELSE NULL END::NUMERIC,
        CASE WHEN (unit_price_ea::TEXT ~ '^[0-9.-]+$') THEN unit_price_ea ELSE NULL END::NUMERIC,
        CASE WHEN (unit_price_null::TEXT ~ '^[0-9.-]+$') THEN unit_price_null ELSE NULL END::NUMERIC,
        CASE WHEN (unit_pricing::TEXT ~ '^[0-9.-]+$') THEN unit_pricing ELSE NULL END::NUMERIC,
        CASE WHEN (unit_price_null::TEXT ~ '^[0-9.-]+$') THEN unit_price_null ELSE NULL END::NUMERIC,
        CASE WHEN (price_net_amount::TEXT ~ '^[0-9.-]+$') THEN price_net_amount ELSE NULL END::NUMERIC
    ) AS net_amount,

     -- Tax
    COALESCE(
        NULLIF(other_tax, '')::NUMERIC,
        NULLIF(other_taxes, '')::NUMERIC,
        NULLIF(other_unit_tax_amount, '')::NUMERIC,
        NULLIF(other_unit_tax, '')::NUMERIC,
        0.00
    ) AS taxes,

    COALESCE(
		case_discount,
		bottle_discount,
		0.00
	
	) as discount,


    -- Quantity
    COALESCE(
        quantity_btl_qty::NUMERIC,
        quantity_cases_delivered,
        other_cases_delivered,
        quantity_case_qty::NUMERIC,
        quantity_full_cases::NUMERIC,
        quantity_item::NUMERIC,
        quantity2::NUMERIC,
        quantity_qty::NUMERIC,
        quantity_cs_pk::NUMERIC,
        quantity_bottles_delivered,
        other_null_quantity::NUMERIC,
        other_btl_qty::NUMERIC,
        other_case_qty::NUMERIC,
        item_null_q::NUMERIC,
        quantity_null::NUMERIC,
        quantity_shipped::NUMERIC, 
        quantity_ordered::NUMERIC, 
		qty_shipped::NUMERIC, 
        0

    ) AS quantity,
	
	price::NUMERIC,
	
	-- Determine unit_of_measure based on boolean fields
    COALESCE(
    uom_bottle,
    uom_case,
    other_null_unit_type,
    CASE
        WHEN bottle_present THEN 'bottle'
        WHEN case_present THEN 'case'
        ELSE CASE
            WHEN quantity2 IS NOT NULL AND quantity2::TEXT ~ '\.\d+' THEN 'lb'
            ELSE 'each'
        END
    END
) AS unit_of_measure,
	
	
	COALESCE(
		quantity_pack::NUMERIC,
    	pk_sz_other_pack::NUMERIC,
        bpc::NUMERIC,
		quantity_null::NUMERIC

	) as pack,


    COALESCE(
		pk_sz_other_size::NUMERIC,
		other_pack_size,
		other_size_quantity_numerator,
		other_size_upper_quantity,
		size_quantity_uom,
		other_gallons_liters
		
	) as size, -- pack size


    COALESCE(
        other_size_unit, 
        other_size_upper_unit,
        size_unit_uom
    ) as unit, -- lowest unit of measure

    COALESCE(
	other_unit_weight::NUMERIC,
	other_extended_weight::NUMERIC
	
	) as weight,

    expense_row,
	-- Track low volume edge cases I skipped here
	quantity_size, 
	quantity_size2

    
FROM 
    ext3_line_item
	

ORDER BY
    in_invoice_processing_id, expense_document_index, line_item_index;