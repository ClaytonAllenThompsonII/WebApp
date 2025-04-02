CREATE OR REPLACE VIEW ext2_line_item AS


SELECT 
    in_invoice_processing_id,
    s3_object_key,
    received_timestamp,
    invoice_receipt_id,
    expense_document_index,
    line_item_index,
    
    -- Extract product code

    COALESCE(
    -- Primary: use PRODUCT_CODE if it’s non-empty
    NULLIF(MAX(CASE WHEN type_text = 'PRODUCT_CODE' THEN vd_text END), ''),
    
    -- Check first for "fuel" in the expense row (case-insensitive)
    CASE 
        WHEN lower(MAX(CASE WHEN type_text = 'EXPENSE_ROW' THEN vd_text END)) LIKE '%fuel%' 
        THEN 'FUEL_CHARGE'
        ELSE NULL
    END,
    
    -- Secondary: if not fuel, attempt to extract digits following "ITEM#:" from EXPENSE_ROW
    CASE 
        WHEN MAX(CASE WHEN type_text = 'EXPENSE_ROW' THEN vd_text END) ~* E'ITEM#:\\s*\\d+' 
        THEN regexp_replace(
                MAX(CASE WHEN type_text = 'EXPENSE_ROW' THEN vd_text END),
                E'.*ITEM#:\\s*(\\d+).*',
                E'\\1',
                'i'
             )
        ELSE NULL
    END,
    
    -- Tertiary: check for type_text = OTHER and ld_text = 'SARASO 21 Item ID'
    NULLIF(MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'SARASO 21 Item ID' THEN vd_text END), ''),
    
    -- Final fallback: if nothing else produced a value, mark as TEXTRACT_FAILURE.
    'TEXTRACT_FAILURE'
) AS product_code,


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
    MAX(CASE WHEN type_text = 'ITEM' AND ld_text = 'Item Description' THEN vd_text ELSE NULL END) AS item_item_description_2,


    -- Extract unit price variations
    MAX(CASE WHEN type_text = 'UNIT_PRICE' THEN vd_text ELSE NULL END) AS unit_price, -- need to add formatting here showing 44-13 instrad of . 
    MAX(CASE WHEN type_text = 'UNIT_PRICE' AND ld_text = 'Price' THEN regexp_replace(vd_text, '-', '.', 'g') ELSE NULL END) AS unit_pricing,
    MAX(CASE WHEN type_text = 'UNIT_PRICE' AND ld_text = 'Price Ea.' THEN vd_text ELSE NULL END) AS unit_price_ea,
    MAX(CASE WHEN type_text = 'UNIT_PRICE' AND ld_text = 'UNIT PRICE' THEN vd_text ELSE NULL END) AS unit_price_upper, -- this is the field that goes with other double entry line item fields. 
    CASE 
        WHEN MAX(CASE WHEN type_text = 'UNIT_PRICE' AND ld_text = 'UNIT PRICE' THEN vd_text ELSE NULL END) IS NOT NULL THEN 
            NULLIF(split_part(MAX(CASE WHEN type_text = 'UNIT_PRICE' AND ld_text = 'UNIT PRICE' THEN vd_text ELSE NULL END), ' ', 1), '')::TEXT
        ELSE NULL
    END AS primary_unit_price_upper,   -- The part we cut off for primary_unit_price_upper: 
    CASE 
        WHEN MAX(CASE WHEN type_text = 'UNIT_PRICE' AND ld_text = 'UNIT PRICE' THEN vd_text ELSE NULL END) IS NOT NULL THEN 
            NULLIF(split_part(MAX(CASE WHEN type_text = 'UNIT_PRICE' AND ld_text = 'UNIT PRICE' THEN vd_text ELSE NULL END), ' ', 2), '')::TEXT
        ELSE NULL
    END AS secondary_unit_price_upper, -- The part we cut off for secondary_unit_price_upper
    CASE 
        WHEN MAX(CASE WHEN type_text = 'UNIT_PRICE' AND ld_text = 'UNIT NET AMOUNT' THEN vd_text ELSE NULL END) ~ '^[0-9.-]+$' THEN
            NULLIF(MAX(CASE WHEN type_text = 'UNIT_PRICE' AND ld_text = 'UNIT NET AMOUNT' THEN vd_text ELSE NULL END), '')::NUMERIC
        ELSE NULL
    END AS unit_net_amount, -- Cast unit_net_amount to numeric
    MAX(CASE WHEN type_text = 'UNIT_PRICE' AND ld_text = 'Unit Price' THEN vd_text ELSE NULL END) AS unit_price_mixed,
    MAX(CASE WHEN type_text = 'UNIT_PRICE' AND ld_text = 'Gross' THEN vd_text ELSE NULL END) AS unit_gross,
    MAX(CASE WHEN type_text = 'UNIT_PRICE' AND ld_text IS NULL THEN vd_text ELSE NULL END) AS unit_price_null,
    MAX(CASE WHEN type_text = 'UNIT_PRICE' AND ld_text = 'UNIT TAX AMOUNT' THEN vd_text ELSE NULL END) AS unit_unit_tax_amount,





    -- Extract total price
    -- Clean price, price_amount, price_net_amount fields by removing non-numeric characters
    MAX(CASE WHEN type_text = 'PRICE' THEN regexp_replace(regexp_replace(vd_text, '-', '.', 'g'), '[^0-9.]', '', 'g') ELSE NULL END) AS price,
    MAX(CASE WHEN type_text = 'PRICE' AND ld_text = 'Amount' THEN regexp_replace(regexp_replace(vd_text, '-', '.', 'g'), '[^0-9.]', '', 'g') ELSE NULL END) AS price_amount,
    MAX(CASE WHEN type_text = 'PRICE' AND ld_text = 'Net Amount' THEN NULLIF(regexp_replace(regexp_replace(vd_text, '-', '.', 'g'), '[^0-9.]', '', 'g'), '')ELSE NULL END)::NUMERIC AS price_net_amount,
    MAX(CASE WHEN type_text = 'PRICE' AND ld_text = 'TOTAL' THEN vd_text ELSE NULL END) AS price_total,
    -- Cast price_extended to numeric
    CASE 
        WHEN MAX(CASE WHEN type_text = 'PRICE' AND ld_text = 'EXTENDED PRICE' THEN vd_text ELSE NULL END) ~ '^[0-9.-]+$' THEN
            NULLIF(MAX(CASE WHEN type_text = 'PRICE' AND ld_text = 'EXTENDED PRICE' THEN vd_text ELSE NULL END), '')::NUMERIC
        ELSE NULL
    END AS price_extended,
    MAX(CASE WHEN type_text = 'PRICE' AND ld_text = 'Extended Price' THEN vd_text ELSE NULL END) AS price_extended_price,
    MAX(CASE WHEN type_text = 'PRICE' AND ld_text IS NULL THEN vd_text ELSE NULL END) AS price_null,

    
    -- Extract quantity
    MAX(CASE WHEN type_text = 'QUANTITY' THEN vd_text ELSE NULL END) as quantity, -- Max Quantity
    MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'Description' THEN vd_text ELSE NULL END) AS quantity_description, -- Do not need downstream
    -- Extract the second number from the `x/x` pattern in the `quantity_item` field
    CASE 
        WHEN MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'ITEM' THEN vd_text ELSE NULL END) IS NOT NULL THEN
            NULLIF(split_part(regexp_replace(
                MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'ITEM' THEN vd_text ELSE NULL END),
                '^(\d+)/(\d+).*',
                '\2'
            ), ' ', 1), '')::NUMERIC
        ELSE NULL
    END AS quantity_item,
    -- Extract quantity variations
    MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'Btl Qty' THEN vd_text ELSE NULL END) AS quantity_btl_qty,
    -- Split quantity_btls_ord_dlv into bottles_ordered and bottles_delivered
    CASE 
        WHEN MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'BTLS ORD/DLV' THEN vd_text ELSE NULL END) IS NOT NULL THEN 
            NULLIF(split_part(MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'BTLS ORD/DLV' THEN vd_text ELSE NULL END), '/', 1), '')::NUMERIC
        ELSE NULL
    END AS quantity_bottles_ordered,
    CASE 
        WHEN MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'BTLS ORD/DLV' THEN vd_text ELSE NULL END) IS NOT NULL THEN 
            NULLIF(split_part(MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'BTLS ORD/DLV' THEN vd_text ELSE NULL END), '/', 2), '')::NUMERIC
        ELSE NULL
    END AS quantity_bottles_delivered,
    -- Split quantity_cs_ord_dlv into cases_ordered and cases_delivered
    CASE 
        WHEN MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'CS ORD/DLV' THEN vd_text ELSE NULL END) IS NOT NULL THEN 
            NULLIF(split_part(MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'CS ORD/DLV' THEN vd_text ELSE NULL END), '/', 1), '')::NUMERIC
        ELSE NULL
    END AS quantity_cases_ordered,
    CASE 
        WHEN MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'CS ORD/DLV' THEN vd_text ELSE NULL END) IS NOT NULL THEN 
            NULLIF(split_part(MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'CS ORD/DLV' THEN vd_text ELSE NULL END), '/', 2), '')::NUMERIC
        ELSE NULL
    END AS quantity_cases_delivered,
    MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'Case Qty' THEN vd_text ELSE NULL END) AS quantity_case_qty,
    MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'Cs/PK' THEN vd_text ELSE NULL END) AS quantity_cs_pk,
    MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'Full Cases' THEN vd_text ELSE NULL END) AS quantity_full_cases,

    -- Clean quantity_pack field by extracting the first numeric value and converting to numeric
    MAX(CASE 
        WHEN type_text = 'QUANTITY' AND ld_text = 'PACK' THEN 
            NULLIF(trim(both ' ' from regexp_replace(vd_text, '[^0-9]', '', 'g')), '')::NUMERIC
        ELSE NULL 
    END) AS quantity_pack,




    MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'Qpc' THEN vd_text ELSE NULL END) AS quantity_qpc,
    MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'Quantity' THEN vd_text ELSE NULL END) AS quantity2, -- this field is actually just weight data from KX Seafood (so far). Consider renaming. 
    -- Clean quantity_qty field by removing all letters and stripping whitespace, then converting to numeric
    MAX(CASE 
        WHEN type_text = 'QUANTITY' AND ld_text = 'QTY' THEN 
            NULLIF(trim(both ' ' from regexp_replace(vd_text, '[A-Za-z]', '', 'g')), '')::NUMERIC
        ELSE NULL 
    END) AS quantity_qty,
    MAX(
    CASE 
        WHEN type_text = 'QUANTITY' AND ld_text IS NULL THEN 
            NULLIF(regexp_replace(vd_text, '[^0-9.]', '', 'g'), '')::NUMERIC 
        ELSE NULL 
    END) AS quantity_null,

    MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'Qty Shipped' THEN vd_text ELSE NULL END) AS qty_shipped,
    MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'Quantity Shipped' THEN vd_text ELSE NULL END) AS quantity_shipped,
    MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'Quantity Ordered' THEN vd_text ELSE NULL END) AS quantity_ordered,

    MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'Size' THEN vd_text ELSE NULL END) AS quantity_size,
    MAX(CASE WHEN type_text = 'QUANTITY' AND ld_text = 'SIZE' THEN vd_text ELSE NULL END) AS quantity_size2,




     -- Extract specific OTHER fields
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Brand' THEN vd_text ELSE NULL END) AS other_brand,
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Bottles' THEN vd_text ELSE NULL END) AS other_bottles, -- useless field; result of summaryField slipping into line items in AWS Textract. 

        -- Update for ext2_line_item to convert other_btl_qty to numeric
    MAX(
        CASE 
            WHEN type_text = 'OTHER' AND ld_text = 'Btl Qty' THEN 
                NULLIF(regexp_replace(vd_text, '[^\d.]', '', 'g'), '')::NUMERIC 
            ELSE 
                NULL 
        END
    ) AS other_btl_qty,
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Btl Price' THEN vd_text ELSE NULL END) AS other_btl_price,
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'BTLS ORD/DLV' THEN vd_text ELSE NULL END) AS other_btls_ord_dlv, -- keep an eye on this see below
  -- Split quantity_cs_ord_dlv into cases_ordered and cases_delivered
    CASE 
        WHEN MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'CS ORD/DLV' THEN vd_text ELSE NULL END) IS NOT NULL THEN 
            NULLIF(split_part(MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'CS ORD/DLV' THEN vd_text ELSE NULL END), '/', 1), '')::NUMERIC
        ELSE NULL
    END AS other_cases_ordered,
    CASE 
        WHEN MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'CS ORD/DLV' THEN vd_text ELSE NULL END) IS NOT NULL THEN 
            NULLIF(split_part(MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'CS ORD/DLV' THEN vd_text ELSE NULL END), '/', 2), '')::NUMERIC
        ELSE NULL
    END AS other_cases_delivered,
    -- Update for ext2_line_item to convert other_case_qty to numeric
    MAX(
        CASE 
            WHEN type_text = 'OTHER' AND ld_text = 'Case Qty' THEN 
                NULLIF(regexp_replace(vd_text, '[^\d.]', '', 'g'), '')::NUMERIC 
            ELSE 
                NULL 
        END
    ) AS other_case_qty,

    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Cs/PK' THEN vd_text ELSE NULL END) AS other_cs_pk, -- this field has no records. Cs/PK seems to be for QUANTITY
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Discount' THEN vd_text ELSE NULL END) AS other_discount,
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Disc Rate' THEN vd_text ELSE NULL END) AS other_disc_rate,
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'DOY' THEN vd_text ELSE NULL END) AS other_doy, -- text field D? 
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Ln' THEN vd_text ELSE NULL END) AS other_ln,

    MAX(CASE 
        WHEN type_text = 'OTHER' AND ld_text = 'Gallons/Liters' THEN 
            NULLIF(regexp_replace(vd_text, '[^\d.]', '', 'g'), '')::NUMERIC
        ELSE 
            NULL 
    END) AS other_gallons_liters,
    
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'PACK' THEN 
            NULLIF(regexp_replace(vd_text, '[^\d.]', '', 'g'), '')::NUMERIC
        ELSE 
            NULL 
        END
    ) AS other_pack_size,
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Pack' THEN vd_text ELSE NULL END) AS other_pack, -- text field D? 
    -- Extract 'other_pack' by getting the numbers before the slash '/' in 'other_pk_size'
    CASE 
        WHEN MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'PK-Size' THEN vd_text ELSE NULL END) IS NOT NULL THEN 
            NULLIF(regexp_replace(split_part(MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'PK-Size' THEN vd_text ELSE NULL END), '/', 1), '[^\d]', '', 'g'), '')::NUMERIC
        ELSE NULL
    END AS pk_sz_other_pack,
    -- Extract 'other_size' by getting the numbers after the slash '/' in 'other_pk_size' and converting '-' to '.'
    CASE 
        WHEN MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'PK-Size' THEN vd_text ELSE NULL END) IS NOT NULL THEN 
            NULLIF(regexp_replace(regexp_replace(split_part(MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'PK-Size' THEN vd_text ELSE NULL END), '/', 2), '-', '.', 'g'), '[^\d.]', '', 'g'), '')::NUMERIC
        ELSE NULL
    END AS pk_sz_other_size,
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Qpc' THEN vd_text ELSE NULL END) AS other_qpc, -- Good as is. 

    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Size' THEN vd_text ELSE NULL END) AS combined_size, 
    -- Split other_size into quantity and unit
    CASE 
    WHEN MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Size' THEN vd_text ELSE NULL END) IS NOT NULL THEN 
        (
            SELECT string_agg(m[1], ' ') 
            FROM regexp_matches(
                MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Size' THEN vd_text ELSE NULL END), 
                '([0-9]+/[0-9]+|[0-9]+)', 
                'g'
            ) AS m
        )
    ELSE NULL
    END AS other_size_quantity,
    CASE 
        WHEN MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Size' THEN vd_text ELSE NULL END) IS NOT NULL THEN 
            (
                SELECT m[1] 
                FROM regexp_matches(
                    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Size' THEN vd_text ELSE NULL END), 
                    '([0-9]+)', 
                    'g'
                ) AS m
                LIMIT 1
            )::NUMERIC
        ELSE NULL
    END AS other_size_quantity_numerator,
    CASE 
        WHEN MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Size' THEN vd_text ELSE NULL END) IS NOT NULL THEN 
            (
                SELECT m[2] 
                FROM regexp_matches(
                    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Size' THEN vd_text ELSE NULL END), 
                    '([0-9]+)/([0-9]+)', 
                    'g'
                ) AS m
                LIMIT 1
            )::NUMERIC
        ELSE NULL
    END AS other_size_quantity_denominator,




    

    CASE 
    WHEN MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Size' THEN vd_text ELSE NULL END) IS NOT NULL THEN 
        CASE 
            WHEN NULLIF(REGEXP_REPLACE(MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Size' THEN vd_text ELSE NULL END), '[^a-zA-Z]', '', 'g'), '') = 'L' THEN 'liters'
            WHEN NULLIF(REGEXP_REPLACE(MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Size' THEN vd_text ELSE NULL END), '[^a-zA-Z]', '', 'g'), '') = 'M' THEN 'milliliters'
            ELSE LOWER(NULLIF(REGEXP_REPLACE(MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Size' THEN vd_text ELSE NULL END), '[^a-zA-Z]', '', 'g'), ''))
        END
    ELSE NULL
    END AS other_size_unit,

    -- Split other_size_upper into quantity and unit
    CASE 
        WHEN MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'SIZE' THEN vd_text ELSE NULL END) IS NOT NULL THEN 
            NULLIF(regexp_replace(MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'SIZE' THEN vd_text ELSE NULL END), '[^0-9.]', '', 'g'), '')::NUMERIC
        ELSE NULL
    END AS other_size_upper_quantity,

    CASE 
        WHEN MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'SIZE' THEN vd_text ELSE NULL END) IS NOT NULL THEN 
            TRIM(LOWER(NULLIF(regexp_replace(MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'SIZE' THEN vd_text ELSE NULL END), '[0-9.]', '', 'g'), '')))
        ELSE NULL
    END AS other_size_upper_unit,

    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Tax' THEN vd_text ELSE NULL END) AS other_tax,
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'TAXES' THEN vd_text ELSE NULL END) AS other_taxes,
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'UNIT TAX AMOUNT' THEN vd_text ELSE NULL END) AS other_unit_tax_amount,
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Unit Tax' THEN vd_text ELSE NULL END) AS other_unit_tax, -- Good checlk .00 entries could impact other fields. 

    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'UNIT NET AMOUNT' THEN vd_text ELSE NULL END) AS other_unit_net_amount, -- Unpack and Handle (done below)
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Unit Net' THEN vd_text ELSE NULL END) AS other_unit_net,

    
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'UNIT PRICE' THEN vd_text ELSE NULL END) AS other_unit_price,

    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'Quantity Ordered' THEN vd_text ELSE NULL END) AS other_quantity_ordered,

    -- Clean other_unit_weight field by removing all letters and stripping whitespace, then converting to numeric
    MAX(CASE 
        WHEN type_text = 'OTHER' AND ld_text = 'Unit Weight' THEN 
            NULLIF(trim(both ' ' from regexp_replace(vd_text, '[^0-9.]', '', 'g')), '')::NUMERIC
        ELSE NULL 
    END) AS other_unit_weight,
    -- Clean other_extended_weight field by removing all letters and stripping whitespace, then converting to numeric
    MAX(CASE 
        WHEN type_text = 'OTHER' AND ld_text = 'Extended Weight' THEN 
            NULLIF(trim(both ' ' from regexp_replace(vd_text, '[^0-9.]', '', 'g')), '')::NUMERIC
        ELSE NULL 
    END) AS other_extended_weight,


    -- Extract and unpack other_unit_disc
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'UNIT DISC' THEN vd_text ELSE NULL END) AS other_unit_disc, -- Unpack primary, secondary
    -- Bottle discount with fallback to case_discount if initial_bottle_discount is null
    CASE
        WHEN 
            CASE 
                WHEN MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'UNIT DISC' THEN vd_text ELSE NULL END) IS NOT NULL THEN 
                    NULLIF(split_part(MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'UNIT DISC' THEN vd_text ELSE NULL END), ' ', 2), '')::NUMERIC
                ELSE NULL
            END IS NULL THEN
                CASE 
                    WHEN MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'UNIT DISC' THEN vd_text ELSE NULL END) IS NOT NULL THEN 
                        NULLIF(split_part(MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'UNIT DISC' THEN vd_text ELSE NULL END), ' ', 1), '')::NUMERIC
                    ELSE NULL
                END
        ELSE
            CASE 
                WHEN MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'UNIT DISC' THEN vd_text ELSE NULL END) IS NOT NULL THEN 
                    NULLIF(split_part(MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'UNIT DISC' THEN vd_text ELSE NULL END), ' ', 2), '')::NUMERIC
                ELSE NULL
            END
    END AS bottle_discount,
    CASE
        WHEN 
            CASE 
                WHEN MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'UNIT DISC' THEN vd_text ELSE NULL END) IS NOT NULL THEN 
                    NULLIF(split_part(MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'UNIT DISC' THEN vd_text ELSE NULL END), ' ', 2), '')::NUMERIC
                ELSE NULL
            END IS NULL THEN
                NULL
        ELSE
            CASE 
                WHEN MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'UNIT DISC' THEN vd_text ELSE NULL END) IS NOT NULL THEN 
                    NULLIF(split_part(MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'UNIT DISC' THEN vd_text ELSE NULL END), ' ', 1), '')::NUMERIC
                ELSE NULL
            END
    END AS case_discount,
   
    -- Split other_unit_net_amount into case_net_amount and bottle_net_amount
    CASE
        WHEN 
            CASE 
                WHEN MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'UNIT NET AMOUNT' THEN vd_text ELSE NULL END) IS NOT NULL THEN 
                    NULLIF(split_part(MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'UNIT NET AMOUNT' THEN vd_text ELSE NULL END), ' ', 2), '')::NUMERIC
                ELSE NULL
            END IS NULL THEN
                CASE 
                    WHEN MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'UNIT NET AMOUNT' THEN vd_text ELSE NULL END) IS NOT NULL THEN 
                        NULLIF(split_part(MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'UNIT NET AMOUNT' THEN vd_text ELSE NULL END), ' ', 1), '')::NUMERIC
                    ELSE NULL
                END
        ELSE
            CASE 
                WHEN MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'UNIT NET AMOUNT' THEN vd_text ELSE NULL END) IS NOT NULL THEN 
                    NULLIF(split_part(MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'UNIT NET AMOUNT' THEN vd_text ELSE NULL END), ' ', 2), '')::NUMERIC
                ELSE NULL
            END
    END AS bottle_net_amount,
    CASE
        WHEN 
            CASE 
                WHEN MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'UNIT NET AMOUNT' THEN vd_text ELSE NULL END) IS NOT NULL THEN 
                    NULLIF(split_part(MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'UNIT NET AMOUNT' THEN vd_text ELSE NULL END), ' ', 2), '')::NUMERIC
                ELSE NULL
            END IS NULL THEN
                NULL
        ELSE
            CASE 
                WHEN MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'UNIT NET AMOUNT' THEN vd_text ELSE NULL END) IS NOT NULL THEN 
                    NULLIF(split_part(MAX(CASE WHEN type_text = 'OTHER' AND ld_text = 'UNIT NET AMOUNT' THEN vd_text ELSE NULL END), ' ', 1), '')::NUMERIC
                ELSE NULL
            END
    END AS case_net_amount,
    -- Extract the original other_null field
    MAX(CASE WHEN type_text = 'OTHER' AND ld_text IS NULL THEN vd_text ELSE NULL END) AS other_null, -- split below, keeping as reminder. 
    -- Split other_null into unit_net_amount, quantity, and unit_type
    CASE
        WHEN MAX(CASE WHEN type_text = 'OTHER' AND ld_text IS NULL THEN vd_text ELSE NULL END) ~ '^[0-9]*\.[0-9]+$' THEN
            NULLIF(MAX(CASE WHEN type_text = 'OTHER' AND ld_text IS NULL THEN vd_text ELSE NULL END), '')::NUMERIC
        ELSE NULL
    END AS other_null_unit_net_amount,

    CASE
        WHEN MAX(CASE WHEN type_text = 'OTHER' AND ld_text IS NULL THEN vd_text ELSE NULL END) ~ '^[0-9]+$' THEN
            NULLIF(MAX(CASE WHEN type_text = 'OTHER' AND ld_text IS NULL THEN vd_text ELSE NULL END), '')::INTEGER
        ELSE NULL
    END AS other_null_quantity,

    CASE
        WHEN MAX(CASE WHEN type_text = 'OTHER' AND ld_text IS NULL THEN vd_text ELSE NULL END) ~ '^[A-Za-z]+$' THEN
            TRIM(LOWER(NULLIF(MAX(CASE WHEN type_text = 'OTHER' AND ld_text IS NULL THEN vd_text ELSE NULL END), '')))
        ELSE NULL
    END AS other_null_unit_type,

    -- Aggregate other details into a JSONB object, ensuring keys are not null
    jsonb_object_agg(
        COALESCE(ld_text, 'Unknown Label'), 
        vd_text
    ) FILTER (WHERE type_text = 'OTHER' AND vd_text IS NOT NULL) AS other_details,
    
    -- Retain expense row information, if available
    MAX(CASE WHEN type_text = 'EXPENSE_ROW' THEN initcap(vd_text) ELSE NULL END) AS expense_row,

    -- Extract the second number after the '/' in the item_null field
CASE
    WHEN MAX(CASE WHEN type_text = 'ITEM' AND ld_text IS NULL THEN regexp_replace(vd_text, '(.*)(ITEM#:.*)', '\1') ELSE NULL END) IS NOT NULL THEN
        CASE
            WHEN regexp_replace(MAX(CASE WHEN type_text = 'ITEM' AND ld_text IS NULL THEN regexp_replace(vd_text, '(.*)(ITEM#:.*)', '\1') ELSE NULL END), '^(\d+)/(\d+).*$', '\2') ~ '^\d+$' THEN
                regexp_replace(MAX(CASE WHEN type_text = 'ITEM' AND ld_text IS NULL THEN regexp_replace(vd_text, '(.*)(ITEM#:.*)', '\1') ELSE NULL END), '^(\d+)/(\d+).*$', '\2')::NUMERIC
            ELSE
                NULL
        END
    ELSE
        NULL
END AS item_null_q -- last resort source of the delivered quantity. 

FROM 
    ext1_line_item
GROUP BY
    in_invoice_processing_id, s3_object_key, invoice_receipt_id, received_timestamp, expense_document_index, line_item_index
ORDER BY
    in_invoice_processing_id, expense_document_index, line_item_index;


