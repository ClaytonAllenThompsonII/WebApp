CREATE OR REPLACE VIEW ext2_vendor AS

WITH vendor_details AS (
    SELECT
        inp.id AS processing_id,
        inp.s3_object_key,
        MAX(
            CASE
                WHEN ((sf.value -> 'Type'::text) ->> 'Text'::text) = 'ACCOUNT_NUMBER'::text THEN (sf.value -> 'ValueDetection'::text) ->> 'Text'::text
                ELSE NULL::text
            END) AS account_number,
        MAX(
            CASE
                WHEN ((sf.value -> 'Type'::text) ->> 'Text'::text) = 'VENDOR_PHONE'::text THEN (sf.value -> 'ValueDetection'::text) ->> 'Text'::text
                ELSE NULL::text
            END) AS vendor_phone,
        MAX(
            CASE
                WHEN ((sf.value -> 'Type'::text) ->> 'Text'::text) = 'VENDOR_URL'::text THEN (sf.value -> 'ValueDetection'::text) ->> 'Text'::text
                ELSE NULL::text
            END) AS vendor_url
    FROM in_invoice_processing inp
    CROSS JOIN LATERAL jsonb_array_elements(((inp.textract_json -> 'ExpenseDocuments'::text) -> 0) -> 'SummaryFields'::text) sf(value)
    GROUP BY inp.id, inp.s3_object_key
)
SELECT
    ext.processing_id,
    ext.s3_object_key,
    ext.type_text,
    ext.type,
    ext.group_text,
    ext.group_type,
    ext.vd_text,
    ext.value_detection,
    ext.ld_text,
    ext.label_detection,
    ext.is_vendor,
    ext.is_vendor_remit_to,
    vd.account_number,
    vd.vendor_phone,
    vd.vendor_url
FROM ext1_vendor ext
JOIN vendor_details vd
    ON ext.processing_id = vd.processing_id
       AND ext.s3_object_key::text = vd.s3_object_key::text;
