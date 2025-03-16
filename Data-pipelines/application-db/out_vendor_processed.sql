
-- local testing using pg admin
psql -h localhost -U your_username -d your_database -c

\copy out_vendor_processed(vendor_id, most_recent_in_invoice_processing_id, most_recent_s3_object_key, most_recent_upload_date, account_number, vendor_name, vendor_short_name, vendor_phone, vendor_address, vendor_street, vendor_city, vendor_state, vendor_zip_code, address_block, vendor_remit_address, remit_to_street, remit_to_city, remit_to_state, remit_to_zip_code, remit_to_address_block, inserted_at, batched_at) FROM '/Users/claytonthompson/Desktop/out_vendor.csv' DELIMITER ',' CSV HEADER NULL AS 'NULL';