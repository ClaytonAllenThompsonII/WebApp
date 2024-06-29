-- Create a view to extract and normalize vendor data from ext1_invoice
CREATE OR REPLACE VIEW ext2_vendor AS

SELECT
    -- Basic metadata fields from ext1_invoice
    in_invoice_processing_id,
    s3_object_key,
    MAX(received_timestamp) AS received_timestamp,
    
    -- Vendor information
    MAX(CASE WHEN summary_type_text = 'ACCOUNT_NUMBER' AND summary_label_text = 'Account Number:' THEN summary_value_text ELSE NULL END) AS account_number_label,
    MAX(CASE WHEN summary_type_text = 'ACCOUNT_NUMBER' AND summary_label_text = 'ACCOUNT#' THEN summary_value_text ELSE NULL END) AS account_number_hash,
	
	-- Customer information
    MAX(CASE WHEN summary_type_text = 'CUSTOMER_NUMBER' AND summary_label_text = 'Customer #' THEN summary_value_text ELSE NULL END) AS customer_number_label,
    MAX(CASE WHEN summary_type_text = 'CUSTOMER_NUMBER' AND summary_label_text = 'CUSTOMER' THEN summary_value_text ELSE NULL END) AS customer_number_customer,
    MAX(CASE WHEN summary_type_text = 'CUSTOMER_NUMBER' AND summary_label_text = 'Customer No' THEN summary_value_text ELSE NULL END) AS customer_no_customer,




    

    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'WD#' THEN summary_value_text ELSE NULL END) AS other_wd_number,


      -- Name information
    MAX(CASE WHEN summary_type_text = 'NAME' AND summary_label_text = 'CUSTOMER:' THEN summary_value_text ELSE NULL END) AS name_customer,
    MAX(CASE WHEN summary_type_text = 'NAME' AND summary_label_text = 'Printed Name:' THEN summary_value_text ELSE NULL END) AS name_printed,
    MAX(CASE WHEN summary_type_text = 'NAME' AND summary_label_text IS NULL THEN summary_value_text ELSE NULL END) AS name_null,

    -- Vendor name
    MAX(CASE WHEN summary_type_text = 'VENDOR_NAME' AND summary_label_text IS NULL THEN summary_value_text ELSE NULL END) AS vendor_name,
    -- Vendor phone
    MAX(CASE WHEN summary_type_text = 'VENDOR_PHONE' AND summary_label_text = 'Phone:' THEN summary_value_text ELSE NULL END) AS vendor_phone,
    MAX(CASE WHEN summary_type_text = 'VENDOR_PHONE' AND summary_label_text = 'Sales Phone:' THEN summary_value_text ELSE NULL END) AS vendor_phone_sales,
    MAX(CASE WHEN summary_type_text = 'VENDOR_PHONE' AND summary_label_text = 'Sales Person:' THEN summary_value_text ELSE NULL END) AS vendor_phone_person,
    MAX(CASE WHEN summary_type_text = 'VENDOR_PHONE' AND summary_label_text IS NULL THEN summary_value_text ELSE NULL END) AS vendor_phone_null,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'LOCAL :' THEN summary_value_text ELSE NULL END) AS other_phone_local,
    
        -- Vendor address
    
    MAX(CASE WHEN summary_type_text = 'VENDOR_ADDRESS' AND summary_label_text IS NULL THEN summary_value_text ELSE NULL END) AS vendor_address_null,


        -- Vendor address fields
    MAX(CASE WHEN summary_type_text = 'NAME' AND group_type = 'vendor' THEN summary_value_text ELSE NULL END) AS name_vendor,
    MAX(CASE WHEN summary_type_text = 'ADDRESS' AND group_type = 'vendor' THEN summary_value_text ELSE NULL END) AS vendor_address,
    MAX(CASE WHEN summary_type_text = 'STREET' AND group_type = 'vendor' THEN summary_value_text ELSE NULL END) AS vendor_street,
    MAX(CASE WHEN summary_type_text = 'CITY' AND group_type = 'vendor' THEN summary_value_text ELSE NULL END) AS vendor_city,
    MAX(CASE WHEN summary_type_text = 'STATE' AND group_type = 'vendor' THEN summary_value_text ELSE NULL END) AS vendor_state,
    MAX(CASE WHEN summary_type_text = 'ZIP_CODE' AND group_type = 'vendor' THEN summary_value_text ELSE NULL END) AS vendor_zip_code,
    MAX(CASE WHEN summary_type_text = 'ADDRESS_BLOCK' AND group_type = 'vendor' THEN summary_value_text ELSE NULL END) AS vendor_address_block,

    -- Remit to address fields
    MAX(CASE WHEN summary_type_text = 'NAME' AND group_type = 'remit_to' THEN summary_value_text ELSE NULL END) AS name_remit_to,
    MAX(CASE WHEN summary_type_text = 'ADDRESS' AND group_type = 'remit_to' THEN summary_value_text ELSE NULL END) AS remit_to_address,
    MAX(CASE WHEN summary_type_text = 'STREET' AND group_type = 'remit_to' THEN summary_value_text ELSE NULL END) AS remit_to_street,
    MAX(CASE WHEN summary_type_text = 'CITY' AND group_type = 'remit_to' THEN summary_value_text ELSE NULL END) AS remit_to_city,
    MAX(CASE WHEN summary_type_text = 'STATE' AND group_type = 'remit_to' THEN summary_value_text ELSE NULL END) AS remit_to_state,
    MAX(CASE WHEN summary_type_text = 'ZIP_CODE' AND group_type = 'remit_to' THEN summary_value_text ELSE NULL END) AS remit_to_zip_code,
    MAX(CASE WHEN summary_type_text = 'ADDRESS_BLOCK' AND group_type = 'remit_to' THEN summary_value_text ELSE NULL END) AS remit_to_address_block,
    MAX(CASE WHEN summary_type_text = 'VENDOR_ADDRESS' AND summary_label_text = 'Please remit payments to:' THEN summary_value_text ELSE NULL END) AS vendor_address_remit_to,
    MAX(CASE WHEN summary_type_text = 'VENDOR_ADDRESS' AND summary_label_text = 'REMIT TO:' THEN summary_value_text ELSE NULL END) AS vendor_address_remit_to_colon,
    MAX(CASE WHEN summary_type_text = 'VENDOR_ADDRESS' AND summary_label_text = 'REMIT TO' THEN summary_value_text ELSE NULL END) AS vendor_address_remit_to_plain,

    -- Ship to address fields
    MAX(CASE WHEN summary_type_text = 'NAME' AND group_type = 'ship_to' THEN summary_value_text ELSE NULL END) AS name_ship_to,
    MAX(CASE WHEN summary_type_text = 'ADDRESS' AND group_type = 'ship_to' THEN summary_value_text ELSE NULL END) AS ship_to_address,
    MAX(CASE WHEN summary_type_text = 'STREET' AND group_type = 'ship_to' THEN summary_value_text ELSE NULL END) AS ship_to_street,
    MAX(CASE WHEN summary_type_text = 'CITY' AND group_type = 'ship_to' THEN summary_value_text ELSE NULL END) AS ship_to_city,
    MAX(CASE WHEN summary_type_text = 'STATE' AND group_type = 'ship_to' THEN summary_value_text ELSE NULL END) AS ship_to_state,
    MAX(CASE WHEN summary_type_text = 'ZIP_CODE' AND group_type = 'ship_to' THEN summary_value_text ELSE NULL END) AS ship_to_zip_code,
    MAX(CASE WHEN summary_type_text = 'ADDRESS_BLOCK' AND group_type = 'ship_to' THEN summary_value_text ELSE NULL END) AS ship_to_address_block,

    -- Sold to address fields
    MAX(CASE WHEN summary_type_text = 'NAME' AND group_type = 'sold_to' THEN summary_value_text ELSE NULL END) AS name_sold_to,
    MAX(CASE WHEN summary_type_text = 'ADDRESS' AND group_type = 'sold_to' THEN summary_value_text ELSE NULL END) AS sold_to_address,
    MAX(CASE WHEN summary_type_text = 'STREET' AND group_type = 'sold_to' THEN summary_value_text ELSE NULL END) AS sold_to_street,
    MAX(CASE WHEN summary_type_text = 'CITY' AND group_type = 'sold_to' THEN summary_value_text ELSE NULL END) AS sold_to_city,
    MAX(CASE WHEN summary_type_text = 'STATE' AND group_type = 'sold_to' THEN summary_value_text ELSE NULL END) AS sold_to_state,
    MAX(CASE WHEN summary_type_text = 'ZIP_CODE' AND group_type = 'sold_to' THEN summary_value_text ELSE NULL END) AS sold_to_zip_code,
    MAX(CASE WHEN summary_type_text = 'ADDRESS_BLOCK' AND group_type = 'sold_to' THEN summary_value_text ELSE NULL END) AS sold_to_address_block,

    -- Bill to address fields
    MAX(CASE WHEN summary_type_text = 'NAME' AND group_type = 'bill_to' THEN summary_value_text ELSE NULL END) AS name_bill_to,
    MAX(CASE WHEN summary_type_text = 'ADDRESS' AND group_type = 'bill_to' THEN summary_value_text ELSE NULL END) AS bill_to_address,
    MAX(CASE WHEN summary_type_text = 'STREET' AND group_type = 'bill_to' THEN summary_value_text ELSE NULL END) AS bill_to_street,
    MAX(CASE WHEN summary_type_text = 'CITY' AND group_type = 'bill_to' THEN summary_value_text ELSE NULL END) AS bill_to_city,
    MAX(CASE WHEN summary_type_text = 'STATE' AND group_type = 'bill_to' THEN summary_value_text ELSE NULL END) AS bill_to_state,
    MAX(CASE WHEN summary_type_text = 'ZIP_CODE' AND group_type = 'bill_to' THEN summary_value_text ELSE NULL END) AS bill_to_zip_code,
    MAX(CASE WHEN summary_type_text = 'ADDRESS_BLOCK' AND group_type = 'bill_to' THEN summary_value_text ELSE NULL END) AS bill_to_address_block,

    -- Receiver address fields
    MAX(CASE WHEN summary_type_text = 'NAME' AND group_type = 'receiver' THEN summary_value_text ELSE NULL END) AS name_receiver,
    MAX(CASE WHEN summary_type_text = 'ADDRESS' AND group_type = 'receiver' THEN summary_value_text ELSE NULL END) AS receiver_address,
    MAX(CASE WHEN summary_type_text = 'STREET' AND group_type = 'receiver' THEN summary_value_text ELSE NULL END) AS receiver_street,
    MAX(CASE WHEN summary_type_text = 'CITY' AND group_type = 'receiver' THEN summary_value_text ELSE NULL END) AS receiver_city,
    MAX(CASE WHEN summary_type_text = 'STATE' AND group_type = 'receiver' THEN summary_value_text ELSE NULL END) AS receiver_state,
    MAX(CASE WHEN summary_type_text = 'ZIP_CODE' AND group_type = 'receiver' THEN summary_value_text ELSE NULL END) AS receiver_zip_code,
    MAX(CASE WHEN summary_type_text = 'ADDRESS_BLOCK' AND group_type = 'receiver' THEN summary_value_text ELSE NULL END) AS receiver_address_block


FROM
    ext1_invoice
GROUP BY
    in_invoice_processing_id, s3_object_key
ORDER BY
    in_invoice_processing_id;
