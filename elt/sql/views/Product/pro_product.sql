-- Create a view to summarize products from line items
WITH product_prices AS (
    SELECT 
        product_code,
        brand,
        item_description,
        quantity,
        unit_price,
        net_amount,
        upload_date,
        unit_of_measure,
        pack,
        size,
        unit,
        FIRST_VALUE(net_amount) OVER (PARTITION BY product_code ORDER BY upload_date DESC) AS most_recent_net_price
    FROM 
        for_line_item
)
SELECT 
    -- Extract the unique product code
    product_code,
    
    -- Aggregate other relevant fields to create a product profile
    MAX(brand) AS brand,
    MAX(item_description) AS description,
    
    -- Calculate aggregated fields
    COUNT(*) AS total_occurrences,
    SUM(quantity) AS total_quantity,
    ROUND(AVG(unit_price), 2) AS average_unit_price,
    
    -- Calculate net price statistics
    ROUND(MAX(net_amount), 2) AS max_net_price,
    ROUND(MIN(net_amount), 2) AS min_net_price,
    ROUND(AVG(net_amount), 2) AS average_net_price,
    ROUND(MODE() WITHIN GROUP (ORDER BY net_amount), 2) AS mode_net_price,
    MAX(upload_date) AS most_recent_date,
    ROUND(MAX(most_recent_net_price), 2) AS most_recent_net_price,

    -- Determine the most common unit of measure
    MODE() WITHIN GROUP (ORDER BY unit_of_measure) AS common_unit_of_measure,
    
    -- Determine the most common pack size and unit
    MODE() WITHIN GROUP (ORDER BY pack) AS common_pack,
    MODE() WITHIN GROUP (ORDER BY size) AS common_size,
    MODE() WITHIN GROUP (ORDER BY unit) AS common_unit

FROM 
    product_prices

-- Group by product code to ensure each product is unique
GROUP BY 
    product_code
ORDER BY 
    product_code;