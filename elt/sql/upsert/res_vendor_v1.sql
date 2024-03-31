INSERT INTO vendor (
  vendor,
  account_number,
  address_block,
  street,
  city,
  state,
  zip_code,
  vendor_phone,
  vendor_url,
  remit_address_block,
  remit_street,
  remit_city,
  remit_state,
  remit_zip_code
)
SELECT 
  DISTINCT v.vendor,
  v.account_number,
  v.address_block,
  v.street,
  v.city,
  v.state,
  v.zip_code,
  v.vendor_phone,
  v.vendor_url,
  v.remit_address_block,
  v.remit_street,
  v.remit_city,
  v.remit_state,
  v.remit_zip_code
FROM ext3_vendor v;
