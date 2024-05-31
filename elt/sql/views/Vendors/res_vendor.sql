CREATE OR REPLACE VIEW res_vendor AS

SELECT
    vendor_name,
    MAX(account_number) AS account_number,
    MAX(vendor_phone) AS vendor_phone,
    MAX(vendor_url) AS vendor_url,
	MAX(vendor_street) AS vendor_street,
	MAX(vendor_city) AS vendor_city,
	MAX(vendor_state) AS vendor_state,
	MAX(vendor_zip_code) AS vendor_zip_code,
	MAX(vendor_address_block) AS vendor_address_block,
    MAX(remit_street) AS remit_street,
    MAX(remit_city) AS remit_city,
    MAX(remit_state) AS remit_state,
    MAX(remit_zip_code) AS remit_zip_code,
    MAX(remit_address_block) AS remit_address_block,
    MAX(sold_street) AS sold_street,
    MAX(sold_city) AS sold_city,
    MAX(sold_state) AS sold_state,
    MAX(sold_zip_code) AS sold_zip_code,
    MAX(sold_address_block) AS sold_address_block,
    MAX(ship_street) AS ship_street,
    MAX(ship_city) AS ship_city,
    MAX(ship_state) AS ship_state,
    MAX(ship_zip_code) AS ship_zip_code,
    MAX(ship_address_block) AS ship_address_block
FROM
    ext2_vendor
GROUP BY
    vendor_name;