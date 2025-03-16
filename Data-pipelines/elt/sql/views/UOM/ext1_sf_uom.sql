/*
    This SQL script is designed to address a specific issue with AWS Textract's processing of invoice data, where certain line item details were incorrectly categorized as summary fields instead of being structured as line items. The script processes these misclassified fields by tagging them under their respective ITEM# identifiers, allowing for a correct association of details such as BPC, Size, and Notes to each item. 

    The purpose of restructuring these data entries is to ensure that the enriched line item details can be effectively integrated with the rest of the invoice data downstream. This adjustment allows for enhanced accuracy and utility in the invoice processing system, facilitating better analysis and reporting capabilities by aligning the extracted data with the expected database schema for invoice management.
*/

CREATE OR REPLACE VIEW ext1_sf_uom AS

WITH summary_fields AS (
    SELECT
        in_invoice_processing_id,
        s3_object_key,
        received_timestamp,
        expense_document_index,
        summary_field_index,
        summary_type_text,
        summary_label_text,
        summary_value_text,
        CASE 
            WHEN summary_label_text = 'ITEM#:' THEN summary_value_text
            ELSE NULL
        END AS item_number
    FROM ext1_invoice
    WHERE summary_type_text = 'OTHER' AND summary_label_text IN ('ITEM#:', 'BPC:', 'SIZE:', 'NOTE:')
),
relevant_fields AS (
    SELECT
        in_invoice_processing_id,
        s3_object_key,
        received_timestamp,
        expense_document_index,
        summary_field_index,
        summary_type_text,
        summary_label_text,
        summary_value_text,
        item_number,
        COUNT(item_number) OVER (PARTITION BY in_invoice_processing_id ORDER BY summary_field_index) AS item_group
    FROM summary_fields
),
grouped_items AS (
    SELECT 
        in_invoice_processing_id,
        s3_object_key,
        received_timestamp,
        expense_document_index,
        item_group,
        MAX(item_number) AS item_number,
        MAX(CASE WHEN summary_label_text = 'BPC:' THEN summary_value_text ELSE NULL END) AS bpc,
        MAX(CASE WHEN summary_label_text = 'SIZE:' THEN summary_value_text ELSE NULL END) AS size,
        MAX(CASE WHEN summary_label_text = 'NOTE:' THEN summary_value_text ELSE NULL END) AS note
    FROM relevant_fields
    GROUP BY 
        in_invoice_processing_id,
        s3_object_key,
        received_timestamp,
        expense_document_index,
        item_group
)
SELECT * 
FROM grouped_items
ORDER BY 
    in_invoice_processing_id, 
    expense_document_index, 
    item_group;