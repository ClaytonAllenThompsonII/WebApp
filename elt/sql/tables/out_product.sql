CREATE TABLE out_product (
    product_id SERIAL PRIMARY KEY,
    product_code TEXT,
    item_description TEXT,
    brand TEXT,
    unit_of_measure TEXT,
    most_recent_unit_price NUMERIC,
    most_recent_net_amount NUMERIC,
    most_recent_taxes NUMERIC,
    most_recent_discount NUMERIC,
    most_recent_quantity NUMERIC,
    most_recent_price NUMERIC,
    most_recent_pack NUMERIC,
    most_recent_size NUMERIC,
    most_recent_unit TEXT,
    most_recent_weight NUMERIC,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (product_code, item_description) -- Ensure uniqueness
);