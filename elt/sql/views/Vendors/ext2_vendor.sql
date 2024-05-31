CREATE OR REPLACE VIEW ext2_vendor AS

WITH vendor_details AS (
    SELECT
        inp.id AS processing_id,
        inp.s3_object_key,
        COALESCE(
			MAX(CASE 
				WHEN sf.value -> 'Type' ->> 'Text' = 'VENDOR_NAME' THEN 
					sf.value -> 'ValueDetection' ->> 'Text' 
			END),
			MAX(CASE 
				WHEN sf.value -> 'Type' ->> 'Text' = 'NAME' AND ev.address_role = 'vendor' THEN 
					sf.value -> 'ValueDetection' ->> 'Text' 
			END)
		) AS vendor_name,
        MAX(CASE WHEN sf.value -> 'Type' ->> 'Text' = 'ACCOUNT_NUMBER' THEN sf.value -> 'ValueDetection' ->> 'Text' END) AS account_number,
        MAX(CASE WHEN sf.value -> 'Type' ->> 'Text' = 'VENDOR_PHONE' THEN sf.value -> 'ValueDetection' ->> 'Text' END) AS vendor_phone,
        MAX(CASE WHEN sf.value -> 'Type' ->> 'Text' = 'VENDOR_URL' THEN sf.value -> 'ValueDetection' ->> 'Text' END) AS vendor_url
    FROM
        in_invoice_processing inp
    JOIN
        LATERAL jsonb_array_elements(inp.textract_json -> 'ExpenseDocuments' -> 0 -> 'SummaryFields') AS sf(value) ON TRUE
    JOIN
        ext1_vendor ev ON ev.processing_id = inp.id AND ev.s3_object_key = inp.s3_object_key
    GROUP BY
        inp.id, inp.s3_object_key
),
address_data AS (
    SELECT *
    FROM ext2_vendor_address_clean
)
SELECT
    vd.processing_id,
    vd.s3_object_key,
    vd.vendor_name,
    vd.account_number,
    vd.vendor_phone,
    vd.vendor_url,


    
    regexp_replace(ad.vendor_street, E'[\\n\\r]+', ' ', 'g'  ) as vendor_street,
    ad.vendor_city,
    ad.vendor_state,
    ad.vendor_zip_code,
    regexp_replace(ad.vendor_address_block, E'[\\n\\r]+', ' ', 'g'  ) as vendor_address_block,

    regexp_replace(ad.remit_street, E'[\\n\\r]+', ' ', 'g' ) as remit_street,
    ad.remit_city,
    ad.remit_state,
    ad.remit_zip_code,
    ad.remit_address_block,
    ad.sold_street,
    ad.sold_city,
    ad.sold_state,
    ad.sold_zip_code,
    ad.sold_address_block,
    ad.ship_street,
    ad.ship_city,
    ad.ship_state,
    ad.ship_zip_code,
    ad.ship_address_block
FROM
    vendor_details vd
JOIN
    address_data ad ON ad.processing_id = vd.processing_id AND ad.s3_object_key = vd.s3_object_key
ORDER BY
    vd.processing_id, vd.s3_object_key;
