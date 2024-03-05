INSERT INTO Vendors (VENDOR_NAME, VENDOR_ADDRESS, VENDOR_PHONE, VENDOR_URL, ADDRESS_BLOCK, STREET, CITY, STATE, COUNTRY, ZIP_CODE)
SELECT 
vendor_name, 
vendor_address, 
vendor_phone, 
vendor_url, 
vendor_address AS ADDRESS_BLOCK,
street,
city, 
state, 
country, 
zip_code

FROM for_vendor
ON CONFLICT (VENDOR_NAME, VENDOR_ADDRESS, VENDOR_PHONE) DO NOTHING;
