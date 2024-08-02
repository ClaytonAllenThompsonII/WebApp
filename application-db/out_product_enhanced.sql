CREATE TABLE out_product_enhanced (
    product_id SERIAL,
    product_code TEXT,
    item_description TEXT,
    brand TEXT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    generated_product_name TEXT,  -- Field for OpenAI generated name
    enhanced_details TEXT,  -- Field for OpenAI enhanced details
    estimated_expiration TEXT,  -- Field for estimated expiration
    UNIQUE (product_code, item_description)  -- Ensure uniqueness
);

-- local testing using pg admin
psql -h localhost -U your_username -d your_database -c 

-- update this file and fields. 
\copy out_product_enhanced(product_id, product_code, item_description, brand, last_updated, generated_product_name, enhanced_details, estimated_expiration) FROM '/Users/claytonthompson/Desktop/out_product_enhanced.csv' DELIMITER ',' CSV HEADER NULL AS 'NULL';