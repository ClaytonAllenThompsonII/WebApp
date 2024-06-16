-- Create a new view ext3_line_item that joins data from ext2_line_item and ext1_sf_uom
CREATE OR REPLACE VIEW ext3_line_item AS
SELECT 
    li.*,  -- Selecting all columns from ext2_line_item
    uom.item_number,  -- Item number from ext1_sf_uom
    uom.bpc,  -- BPC field from ext1_sf_uom
    uom.size,  -- Size field from ext1_sf_uom
    uom.note,  -- Note field from ext1_sf_uom

    -- Unpack size field into size_quantity_uom and size_unit_uom
    CASE 
        WHEN uom.size IS NOT NULL THEN 
            -- Extract numeric part of the size, removing any non-numeric characters
            NULLIF(regexp_replace(uom.size, '[^0-9.]', '', 'g'), '')::NUMERIC
        ELSE NULL
    END AS size_quantity_uom,  -- Numeric quantity part of the size


    CASE 
    WHEN uom.size IS NOT NULL THEN 
        -- Extract unit part of the size, removing any numeric characters and converting to lowercase
        LOWER(NULLIF(regexp_replace(uom.size, '[0-9.]', '', 'g'), ''))
    ELSE NULL
END AS size_unit_uom,


      -- Boolean field to indicate the presence of bottles
    CASE 
        WHEN 
            li.quantity_btl_qty IS NOT NULL OR 
            li.quantity_bottles_ordered IS NOT NULL OR 
            li.quantity_bottles_delivered IS NOT NULL OR
            li.quantity_item IS NOT NULL OR -- need to check if these are causing errors
            li.item_null_q IS NOT NULL -- need to check if these are cuasing errors. 
        THEN TRUE ELSE FALSE 
    END AS bottle_present,

    -- Boolean field to indicate the presence of cases
    CASE 
        WHEN 
            li.quantity_case_qty IS NOT NULL OR 
            li.quantity_cases_delivered IS NOT NULL OR 
            li.quantity_cs_pk IS NOT NULL OR 
            li.other_cases_delivered IS NOT NULL OR 
            li.other_case_qty IS NOT NULL OR
            li.quantity_full_cases IS NOT NULL
        THEN TRUE ELSE FALSE 
    END AS case_present,

     -- UOM fields
    CASE 
        WHEN 
            li.quantity_btl_qty IS NOT NULL OR 
            li.quantity_bottles_ordered IS NOT NULL OR 
            li.quantity_bottles_delivered IS NOT NULL 
        THEN 'bottle' ELSE NULL 
    END AS uom_bottle,

    CASE 
        WHEN 
            li.quantity_case_qty IS NOT NULL OR 
            li.quantity_cases_delivered IS NOT NULL OR 
            li.quantity_cs_pk IS NOT NULL OR 
            li.other_cases_delivered IS NOT NULL OR 
            li.other_case_qty IS NOT NULL 
        THEN 'case' ELSE NULL 
    END AS uom_case


FROM  
    -- Source table ext2_line_item
    ext2_line_item AS li

-- Left join to include all records from ext2_line_item and matching records from ext1_sf_uom
LEFT JOIN 
    ext1_sf_uom AS uom
ON 
    -- Join on in_invoice_processing_id to match invoices
    li.in_invoice_processing_id = uom.in_invoice_processing_id AND
    -- Join on product_code and item_number to match items
    li.product_code = uom.item_number;

-- Add comments explaining each part of the query

/*
This query creates a new view, ext3_line_item, by joining the ext2_line_item and ext1_sf_uom tables. The purpose of this view is to enrich the data in ext2_line_item with additional information from ext1_sf_uom, specifically the fields: item_number, bpc, size, and note. Additionally, it unpacks the size field into two separate fields: size_quantity_uom and size_unit_uom.

1. SELECT li.*, uom.item_number, uom.bpc, uom.size, uom.note:
   - This selects all columns from the ext2_line_item table and adds the item_number, bpc, size, and note columns from the ext1_sf_uom table.

2. Unpack size into size_quantity_uom and size_unit_uom:
   - The first CASE statement extracts the numeric part of the size field, removing any non-numeric characters, and assigns it to size_quantity_uom.
   - The second CASE statement extracts the unit part of the size field, removing any numeric characters, and assigns it to size_unit_uom.

3. FROM ext2_line_item AS li:
   - This specifies that the main data source is the ext2_line_item table, aliased as li.

4. LEFT JOIN ext1_sf_uom AS uom:
   - This performs a left join with the ext1_sf_uom table, aliased as uom, to include all records from ext2_line_item and the matching records from ext1_sf_uom.

5. ON li.in_invoice_processing_id = uom.in_invoice_processing_id AND li.product_code = uom.item_number:
   - This specifies the join condition, matching the in_invoice_processing_id from both tables and the product_code from ext2_line_item with the item_number from ext1_sf_uom.

Overall, this query enriches the ext2_line_item data with additional information from ext1_sf_uom and unpacks the size field into two separate fields for better analysis and reporting.
*/