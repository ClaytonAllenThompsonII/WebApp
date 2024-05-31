-- This is for LTD data. 
-- Ex. Total Quantiy is the sum of all line item qunatities of a distinct item. 




SELECT 
	distinct item AS product_name,
    product_code,
    MAX(Brand) AS brand_name,  -- Assuming brand does not change per product code; adjust if needed.
    item_short,

    -- Cost Details
    SUM(unit_price) as unit_price_LTD,
    ROUND(AVG(unit_price), 2) AS avg_unit_price,
    MIN(unit_price) AS min_unit_price,
    MAX(unit_price) AS max_unit_price,
    MODE() WITHIN GROUP (ORDER BY uom_size_numeric) AS most_common_uom_size,  -- Finds the most common UOM size for the product.
	MAX(Bottle_Price) as Bottle_Price,

    MAX(unit_net_amount) as max_unit_net_amount,
    MIN(unit_net_amount) as min_unit_net_amount,

    MAX(price) as max_price,
    MIN(price) as min_price, 


    SUM(quantity) as total_quantity
FROM 
    ext3_line_item
GROUP BY 
    product_code, item, item_short
ORDER BY 
    product_code;