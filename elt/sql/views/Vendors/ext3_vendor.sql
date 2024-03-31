CREATE OR REPLACE VIEW ext3_vendor AS

WITH vendor_data AS (
  SELECT
    processing_id,
    s3_object_key,
    MAX(account_number) AS account_number,
    MIN(vendor_phone) AS vendor_phone,
    MIN(vendor_url) AS vendor_url,
                                                                                                                          
    -- Strip trailing whitespaces from vendor name
    TRIM(TRAILING FROM MAX(CASE WHEN type_text = 'NAME' AND is_vendor = TRUE THEN VD_text END))            AS vendor,

    -- Remove trailing commas, periods from city and state
    RTRIM(
      MAX(CASE WHEN type_text = 'ADDRESS' AND is_vendor = TRUE THEN VD_text END),
       ',' || '.')          AS address,

    -- Need to ADD LOGIC to only return address type_text where group_type = Vendor

    MAX(CASE WHEN type_text = 'STREET' AND is_vendor = TRUE THEN VD_text END)                              AS street,

    -- Convert city to title case (capitalize first letter of each word)
    INITCAP(RTRIM(MAX(CASE WHEN type_text = 'CITY' AND is_vendor = TRUE THEN VD_text END),',' || '.'))     AS city,
    -- Convert state to uppercase
    UPPER(RTRIM(MAX(CASE WHEN type_text = 'STATE' AND is_vendor = TRUE THEN VD_text END), ',' || '.'))                AS state,

    MAX(CASE WHEN type_text = 'ZIP_CODE' AND is_vendor = TRUE THEN VD_text END)                                       AS zip_code,
    
    MAX(CASE WHEN type_text = 'ADDRESS_BLOCK' AND is_vendor = TRUE THEN VD_text END)                                  AS address_block,

    -- Remittance Address deetails
    MAX(CASE WHEN type_text = 'ADDRESS_BLOCK' AND is_vendor_remit_to = TRUE THEN VD_text END)                           AS remit_address_block,
	  MAX(CASE WHEN type_text = 'STREET' AND is_vendor_remit_to = TRUE THEN VD_text END)                                  AS remit_street,

	  INITCAP(RTRIM(
      MAX(CASE WHEN type_text = 'CITY' AND is_vendor_remit_to = TRUE THEN VD_text END),
      ',' || '.'
     ))                                                                                                                AS remit_city,
	 -- Convert state to uppercase
    UPPER(RTRIM(
      MAX(CASE WHEN type_text = 'STATE' AND is_vendor_remit_to = TRUE THEN VD_text END),
      ',' || '.'
     ))                                                                                                                AS remit_state,
		MAX(CASE WHEN type_text = 'ZIP_CODE' AND is_vendor_remit_to = TRUE THEN VD_text END)                              as remit_zip_code
	

  FROM ext2_vendor
  
  GROUP BY processing_id, s3_object_key
),

completed_data AS (
  SELECT
    v.vendor,
    v.account_number,
    COALESCE(v.address_block,
             (
               SELECT vd2.address_block
               FROM vendor_data vd2
               WHERE vd2.vendor = v.vendor
                     AND vd2.address_block IS NOT NULL
               ORDER BY vd2.processing_id, vd2.s3_object_key
               DESC
               LIMIT 1
             )
           ) AS address_block,
    -- Apply COALESCE for other missing fields as needed
	COALESCE(v.street,
             (
               SELECT vd2.street
               FROM vendor_data vd2
               WHERE vd2.vendor = v.vendor
                     AND vd2.street IS NOT NULL
               ORDER BY vd2.processing_id, vd2.s3_object_key
               DESC
               LIMIT 1
             )
           ) AS street,
	COALESCE(v.city,
             (
               SELECT vd2.city
               FROM vendor_data vd2
               WHERE vd2.vendor = v.vendor
                     AND vd2.city IS NOT NULL
               ORDER BY vd2.processing_id, vd2.s3_object_key
               DESC
               LIMIT 1
             )
           ) AS city,
    COALESCE(v.state,
             (
               SELECT vd2.state
               FROM vendor_data vd2
               WHERE vd2.vendor = v.vendor
                     AND vd2.state IS NOT NULL
               ORDER BY vd2.processing_id, vd2.s3_object_key
               DESC
               LIMIT 1
             )
           ) AS state,
	
    
    v.zip_code,
    v.vendor_phone,
    v.vendor_url,
    v.remit_address_block,
    v.remit_street,
    v.remit_city,
    v.remit_state,
    v.remit_zip_code
  FROM vendor_data v
  ORDER BY vendor, processing_id, s3_object_key
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
FROM completed_data v;