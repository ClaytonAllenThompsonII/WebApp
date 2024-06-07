-- Create the vendor table
CREATE TABLE out_vendor (
    vendor_id SERIAL PRIMARY KEY,                            -- Auto-incrementing primary key
    most_recent_in_invoice_processing_id INT,                -- Foreign key to track the source of the most recent vendor record
    most_recent_s3_object_key VARCHAR(255),                  -- S3 key for locating the most recent invoice document
    most_recent_upload_date TIMESTAMP,                       -- Timestamp when the most recent vendor record was uploaded
    account_number VARCHAR(255),                             -- Vendor's account number
    vendor_name VARCHAR(255),                                -- Vendor's name
    vendor_phone VARCHAR(15),                                -- Vendor's phone number
    vendor_address VARCHAR(255),                             -- Vendor's address
    vendor_street VARCHAR(255),                              -- Vendor's street address
    vendor_city VARCHAR(255),                                -- Vendor's city
    vendor_state VARCHAR(2),                                 -- Vendor's state
    vendor_zip_code VARCHAR(10),                             -- Vendor's ZIP code
    address_block TEXT,                                      -- Vendor's address block
    vendor_remit_address VARCHAR(255),                       -- Vendor's remit-to address
    remit_to_street VARCHAR(255),                            -- Remit-to street address
    remit_to_city VARCHAR(255),                              -- Remit-to city
    remit_to_state VARCHAR(2),                               -- Remit-to state
    remit_to_zip_code VARCHAR(10),                           -- Remit-to ZIP code
    remit_to_address_block TEXT,                             -- Remit-to address block
    inserted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,-- Timestamp when the record is inserted into this table
    batched_at TIMESTAMP,                           -- Timestamp when the record is batched into the application database
    UNIQUE (vendor_name, vendor_phone)                       -- Ensure unique vendor records based on name and phone
);