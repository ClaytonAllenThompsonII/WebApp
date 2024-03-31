
CREATE TABLE vendor (
  vendor_id SERIAL PRIMARY KEY,  -- Auto-incrementing ID as primary key
  vendor VARCHAR(255) NOT NULL UNIQUE,  -- Unique vendor name
  account_number VARCHAR(255),
  address_block TEXT,
  street VARCHAR(255),
  city VARCHAR(255),
  state VARCHAR(255),
  zip_code VARCHAR(255),
  vendor_phone VARCHAR(255),
  vendor_url VARCHAR(255),
  remit_address_block TEXT,
  remit_street VARCHAR(255),
  remit_city VARCHAR(255),
  remit_state VARCHAR(255),
  remit_zip_code VARCHAR(255)
);