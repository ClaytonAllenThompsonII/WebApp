CREATE OR REPLACE VIEW view_distinct_vendorsAS 
SELECT
  MAX(processing_id) AS last_processing_id, -- This should reference the field correctly now.
  vendor_name,
  vendor_address,
  MAX(city) AS city, -- Aggregating these under the assumption they're consistent per vendor.
  MAX(state) AS state,
  MAX(zip_code) AS zip_code,
  MAX(vendor_url) AS vendor_url,
  MAX(vendor_phone) AS vendor_phone,
  MAX(account_number) AS account_number
  
FROM
  view_vendor_details
GROUP BY
  vendor_name, vendor_address
ORDER BY
  vendor_name, vendor_address;