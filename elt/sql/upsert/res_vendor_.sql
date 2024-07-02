-- NEED TO ADD A CURRENT_TIME_STAMP for batch and insert processing... 

-- Upsert script for inserting or updating records in the vendor table

-- Insert into the out_vendor table
INSERT INTO out_vendor (
    most_recent_in_invoice_processing_id,  -- ID of the most recent invoice processing record
    most_recent_s3_object_key,             -- S3 key for locating the most recent invoice document
    most_recent_upload_date,               -- Timestamp when the most recent vendor record was uploaded
    account_number,                        -- Vendor's account number
    vendor_name,                           -- Vendor's name
    vendor_phone,                          -- Vendor's phone number
    vendor_address,                        -- Vendor's address
    vendor_street,                         -- Vendor's street address
    vendor_city,                           -- Vendor's city
    vendor_state,                          -- Vendor's state
    vendor_zip_code,                       -- Vendor's ZIP code
    address_block,                         -- Vendor's address block
    vendor_remit_address,                  -- Vendor's remit-to address
    remit_to_street,                       -- Remit-to street address
    remit_to_city,                         -- Remit-to city
    remit_to_state,                        -- Remit-to state
    remit_to_zip_code,                     -- Remit-to ZIP code
    remit_to_address_block,                 -- Remit-to address block
    inserted_at,                           -- Timestamp when the record is inserted into this table
    batched_at                             -- Timestamp when the record is batched into the application database (initially NULL)
)
SELECT 
    most_recent_in_invoice_processing_id,
    most_recent_s3_object_key,
    most_recent_upload_date,
    account_number,
    vendor_name,
    vendor_phone,
    vendor_address,
    vendor_street,
    vendor_city,
    vendor_state,
    vendor_zip_code,
    address_block,
    vendor_remit_address,
    remit_to_street,
    remit_to_city,
    remit_to_state,
    remit_to_zip_code,
    remit_to_address_block,
    CURRENT_TIMESTAMP,                    -- Set the inserted_at timestamp to the current time
    NULL 
FROM 
    pro_vendor  -- View containing distinct vendors with the most recent records

-- On conflict (i.e., if a record with the same vendor_name and vendor_phone already exists)
-- Update the existing record with the new data
ON CONFLICT (vendor_name, account_number) -- tough to match on vendor_phone... need to make sure these fields are rock solid. 
DO UPDATE SET
    most_recent_in_invoice_processing_id = EXCLUDED.most_recent_in_invoice_processing_id,  -- Update to the most recent invoice processing ID
    most_recent_s3_object_key = EXCLUDED.most_recent_s3_object_key,                        -- Update to the most recent S3 object key
    most_recent_upload_date = EXCLUDED.most_recent_upload_date,                            -- Update to the most recent upload date
    account_number = EXCLUDED.account_number,                                              -- Update account number
    vendor_address = EXCLUDED.vendor_address,                                              -- Update vendor address
    vendor_street = EXCLUDED.vendor_street,                                                -- Update vendor street
    vendor_city = EXCLUDED.vendor_city,                                                    -- Update vendor city
    vendor_state = EXCLUDED.vendor_state,                                                  -- Update vendor state
    vendor_zip_code = EXCLUDED.vendor_zip_code,                                            -- Update vendor ZIP code
    address_block = EXCLUDED.address_block,                                                -- Update address block
    vendor_remit_address = EXCLUDED.vendor_remit_address,                                  -- Update vendor remit-to address
    remit_to_street = EXCLUDED.remit_to_street,                                            -- Update remit-to street
    remit_to_city = EXCLUDED.remit_to_city,                                                -- Update remit-to city
    remit_to_state = EXCLUDED.remit_to_state,                                              -- Update remit-to state
    remit_to_zip_code = EXCLUDED.remit_to_zip_code,                                        -- Update remit-to ZIP code
    remit_to_address_block = EXCLUDED.remit_to_address_block,                              -- Update remit-to address block
    inserted_at = EXCLUDED.inserted_at,                                                    -- Update inserted_at timestamp
    batched_at = EXCLUDED.batched_at;                                                      -- Preserve batched_at timestamp if it exists
