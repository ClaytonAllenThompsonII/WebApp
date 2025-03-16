-- Create a view to extract multiple instances of weight fields from ext1_invoice and split the total_weight field
WITH extracted_fields AS (
    SELECT
        in_invoice_processing_id,
        s3_object_key,
        received_timestamp,
		expense_document_index,           -- Index of the expense document in the JSON array
    	summary_field_index, 
        CASE 
            WHEN summary_label_text = 'ITEM#:' THEN summary_value_text
            ELSE NULL
        END AS item_number,
        -- Extract and split the total_weight field

        CASE WHEN summary_label_text = 'TOT WT:' THEN summary_value_text ELSE NULL END AS tot_wt,
        CASE 
            WHEN summary_label_text = 'TOT WT:' THEN split_part(summary_value_text, ' ', 1)
            ELSE NULL
        END AS total_weight,
        CASE 
            WHEN summary_label_text = 'TOT WT:' THEN split_part(summary_value_text, ' ', 2)
            ELSE NULL
        END AS summary_field_price,
        CASE 
            WHEN summary_label_text = 'TOT WT:' THEN split_part(summary_value_text, ' ', 3)
            ELSE NULL
        END AS summary_field_amount,
        -- Keep the t_weight field as is
        CASE 
            WHEN summary_label_text = 'T/WT=' THEN summary_value_text
            ELSE NULL
        END AS t_weight,
        -- Include other relevant fields
        MAX(CASE WHEN summary_type_text = 'VENDOR_NAME' AND summary_label_text IS NULL THEN summary_value_text ELSE NULL END) OVER (PARTITION BY in_invoice_processing_id) AS vendor_name,
        MAX(CASE WHEN summary_type_text = 'INVOICE_RECEIPT_ID' AND summary_label_text = 'Invoice #' THEN summary_value_text ELSE NULL END) OVER (PARTITION BY in_invoice_processing_id) AS invoice_receipt_id_number,
        MAX(CASE WHEN summary_type_text = 'INVOICE_RECEIPT_ID' AND summary_label_text = 'INVOICE' THEN summary_value_text ELSE NULL END) OVER (PARTITION BY in_invoice_processing_id) AS invoice_receipt_id_invoice,
        MAX(CASE WHEN summary_type_text = 'INVOICE_RECEIPT_ID' AND summary_label_text = 'Invoice Number:' THEN summary_value_text ELSE NULL END) OVER (PARTITION BY in_invoice_processing_id) AS invoice_receipt_id_label,
        MAX(CASE WHEN summary_type_text = 'INVOICE_RECEIPT_ID' AND summary_label_text = 'INVOICE NUMBER' THEN summary_value_text ELSE NULL END) OVER (PARTITION BY in_invoice_processing_id) AS invoice_receipt_id_number_upper,
        MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'WD#' THEN summary_value_text ELSE NULL END) OVER (PARTITION BY in_invoice_processing_id) AS other_wd_number
    FROM
        ext1_invoice
    WHERE
        summary_label_text IN ('ITEM#:', 'TOT WT:', 'T/WT=')
)
SELECT
    in_invoice_processing_id,
	expense_document_index,           -- Index of the expense document in the JSON array
    	summary_field_index,
    s3_object_key,
    received_timestamp,
    item_number,
    total_weight::NUMERIC,
    summary_field_price::NUMERIC,
    summary_field_amount::NUMERIC,
    t_weight,
    tot_wt,
    vendor_name,
    invoice_receipt_id_number,
    invoice_receipt_id_invoice,
    invoice_receipt_id_label,
    invoice_receipt_id_number_upper,
    other_wd_number
FROM
    extracted_fields
WHERE
    total_weight IS NOT NULL OR t_weight IS NOT NULL
ORDER BY
    in_invoice_processing_id, s3_object_key, item_number;