/*
    This SQL script is designed to address a specific issue with AWS Textract's processing of invoice data, where certain line item details were incorrectly categorized as summary fields instead of being structured as line items. The script processes these misclassified fields by tagging them under their respective ITEM# identifiers, allowing for a correct association of details such as BPC, Size, and Notes to each item. 

    The purpose of restructuring these data entries is to ensure that the enriched line item details can be effectively integrated with the rest of the invoice data downstream. This adjustment allows for enhanced accuracy and utility in the invoice processing system, facilitating better analysis and reporting capabilities by aligning the extracted data with the expected database schema for invoice management.
*/

CREATE OR REPLACE VIEW ext1_uom AS

-- CTE `other`: Extracts each SummaryField from the Textract JSON stored in the database, filtering for types labeled as 'OTHER'.
WITH other AS (
    SELECT
        inp.id AS invoice_id,  -- Unique identifier for the invoice
        inp.s3_object_key,  -- Reference to the S3 object where the original document is stored
        sf.idx AS field_index,  -- Index of the field within the SummaryFields array
        sf.value ->> 'Type' AS field_type,  -- Type of the field
        sf.value -> 'Type' ->> 'Text' AS field_text,  -- Text description of the field type
        sf.value -> 'ValueDetection' ->> 'Text' AS summary_value_text,  -- Detected text of the summary value
        sf.value -> 'LabelDetection' ->> 'Text' AS summary_label_text  -- Label text associated with the value
    FROM
        in_invoice_processing inp,
        LATERAL jsonb_array_elements(inp.textract_json -> 'ExpenseDocuments' -> 0 -> 'SummaryFields') WITH ORDINALITY AS sf(value, idx)
    WHERE
        sf.value -> 'Type' ->> 'Text' = 'OTHER'  -- Filter to only include fields marked as 'OTHER'
),

-- CTE `relevant_fields`: Marks each 'ITEM#:' entry with its value for grouping purposes.
relevant_fields AS (
    SELECT
        invoice_id,
        s3_object_key,
        field_index,
        field_type,
        field_text,
        summary_value_text,
        summary_label_text,
        CASE 
            WHEN summary_label_text = 'ITEM#:' THEN summary_value_text
            ELSE NULL
        END AS item_number  -- Captures the item number if the field is 'ITEM#:'
    FROM
        other
),

-- CTE `item_groups`: Assigns a group identifier to each set of fields starting from an 'ITEM#:' field.
item_groups AS (
    SELECT *,
           COUNT(item_number) OVER (PARTITION BY invoice_id ORDER BY field_index) AS group_id  -- Assign a group ID based on item number appearance
    FROM relevant_fields
),

-- CTE `tagged_items`: Propagates the item number across subsequent records until the next 'ITEM#:' field.
tagged_items AS (
    SELECT
        invoice_id,
        s3_object_key,
        field_index,
        field_type,
        field_text,
        summary_value_text,
        summary_label_text,
        MAX(item_number) OVER (PARTITION BY invoice_id, group_id ORDER BY field_index ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS line_item_product_group
    FROM item_groups
)

-- Final SELECT: Aggregates data into a pivoted format, pulling out the 'BPC:', 'SIZE:', and 'NOTE:' values for each item group.
SELECT
    invoice_id,
    s3_object_key,
    line_item_product_group as product_number,
    MAX(CASE WHEN summary_label_text = 'BPC:' THEN summary_value_text ELSE NULL END) AS BPC,  -- Maximum value for BPC within the group
    MAX(CASE WHEN summary_label_text = 'SIZE:' THEN summary_value_text ELSE NULL END) AS Size,  -- Maximum value for Size within the group
    MAX(CASE WHEN summary_label_text = 'NOTE:' THEN summary_value_text ELSE NULL END) AS Note  -- Maximum value for Note within the group
FROM tagged_items
WHERE line_item_product_group IS NOT NULL AND summary_label_text <> 'ITEM#:'  -- Exclude the 'ITEM#:' labels from the output
GROUP BY invoice_id, s3_object_key, line_item_product_group  -- Group by invoice and line item group
ORDER BY invoice_id, line_item_product_group;  -- Order results by invoice and item group