CREATE OR REPLACE VIEW ext2_line_item AS

SELECT 
    in_invoice_processing_id,
    s3_object_key,
    received_timestamp,
    line_item_index,
    MAX(CASE WHEN type_text = 'PRODUCT_CODE' THEN vd_text ELSE NULL END) AS product_code,
	MAX(CASE WHEN type_text = 'ITEM' THEN vd_text ELSE NULL END) AS item,
    MAX(CASE WHEN type_text = 'UNIT_PRICE' THEN vd_text ELSE NULL END) AS unit_price,
	MAX(CASE WHEN type_text = 'OTHER' THEN vd_text ELSE NULL END) AS max_other,
    MAX(CASE WHEN type_text = 'PRICE' THEN vd_text ELSE NULL END) AS price,
    
	MAX(CASE WHEN type_text = 'EXPENSE_ROW' THEN vd_text ELSE NULL END) AS expense_row
   
    
FROM 
    ext1_line_item
GROUP BY
    in_invoice_processing_id, s3_object_key, received_timestamp, line_item_index
ORDER BY
    in_invoice_processing_id, line_item_index;



COMMENT ON VIEW ext2_line_item IS $$
This view aggregates data from the 'ext1_line_item' view by transforming 'type_text' values into distinct columns for each 'line_item_index'. Each line item index groups related attributes from the source document, facilitating structured data analysis and reporting. The view specifically aggregates:
- 'product_code': Derived from 'PRODUCT_CODE' entries in 'type_text'.
- 'item': Extracted from 'ITEM' type_text entries.
- 'unit_price': Pulled from 'UNIT_PRICE' type_text entries.
- 'max_other': A maximum (or latest if dates/times involved) 'vd_text' value from entries classified as 'OTHER' in 'type_text'. This helps consolidate various 'OTHER' descriptions into a single column.
- 'price': Represents the maximum 'vd_text' extracted from 'PRICE' type_text entries.
- 'expense_row': Captures expense details from 'EXPENSE_ROW' type_text, providing a comprehensive expense summary.

Grouping is performed by invoice processing IDs, S3 object keys, receipt timestamps, and line item indices to ensure coherent aggregation of data per item. The view is crucial for downstream processes that require organized and accessible data for further analytics, reporting, or transformations.
$$;

