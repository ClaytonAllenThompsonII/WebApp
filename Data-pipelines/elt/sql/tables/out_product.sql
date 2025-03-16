DROP TABLE IF EXISTS out_product CASCADE;

DROP TABLE IF EXISTS out_product CASCADE;

-- Recreate the out_product table with the brand column and optional fields
-- Recreate the out_product table without a foreign key for classification_id
CREATE TABLE out_product (
    product_id SERIAL PRIMARY KEY,             -- Auto-incrementing primary key
    product_code TEXT,                         -- Product code can now be NULL
    item_description TEXT,                     -- Item description can now be NULL
    brand TEXT,                                -- Optional brand column
    classification_id INT,                     -- Classification field (optional, will be NULL initially)
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Automatically set on creation
    UNIQUE (product_code, item_description, brand)    -- Ensure uniqueness across these fields
);