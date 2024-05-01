
CREATE TABLE out_vendor (
    vendor_id SERIAL PRIMARY KEY,  -- Auto-incrementing ID as primary key
    vendor_name VARCHAR(255) UNIQUE,  -- Unique vendor name
    account_number VARCHAR(255),
    vendor_phone VARCHAR(255),
    vendor_url VARCHAR(255),
    remit_street VARCHAR(255),
    remit_city VARCHAR(255),
    remit_state VARCHAR(255),
    remit_zip_code VARCHAR(255),
    remit_address_block TEXT,
    sold_street VARCHAR(255),
    sold_city VARCHAR(255),
    sold_state VARCHAR(255),
    sold_zip_code VARCHAR(255),
    sold_address_block TEXT,
    ship_street VARCHAR(255),
    ship_city VARCHAR(255),
    ship_state VARCHAR(255),
    ship_zip_code VARCHAR(255),
    ship_address_block TEXT
);