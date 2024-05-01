CREATE OR REPLACE VIEW ext2_invoice AS

SELECT
    in_invoice_processing_id,
    s3_object_key,
    MAX(received_timestamp) AS received_timestamp,
    MAX(CASE WHEN summary_type_text = 'INVOICE_RECEIPT_DATE' THEN summary_value_text END) AS invoice_receipt_date,
    MAX(CASE WHEN summary_type_text = 'INVOICE_RECEIPT_ID' THEN summary_value_text END) AS invoice_receipt_id,
    MAX(CASE WHEN summary_type_text = 'ACCOUNT_NUMBER' THEN summary_value_text END) AS account_number,
    MAX(CASE WHEN summary_type_text = 'VENDOR_NAME' OR (summary_type_text = 'NAME' AND group_property_id = 'Vendor Group') THEN summary_value_text END) AS vendor_name,
    MAX(CASE WHEN summary_type_text = 'ORDER_DATE' THEN summary_value_text END) AS order_date,
    MAX(CASE WHEN summary_type_text = 'DUE_DATE' THEN summary_value_text END) AS due_date,
    MAX(CASE WHEN summary_type_text = 'DELIVERY_DATE' THEN summary_value_text END) AS delivery_date,
    MAX(CASE WHEN summary_type_text = 'PO_NUMBER' THEN summary_value_text END) AS po_number,
    MAX(CASE WHEN summary_type_text = 'PAYMENT_TERMS' THEN summary_value_text END) AS payment_terms,
    MAX(CASE WHEN summary_type_text = 'TOTAL' THEN summary_value_text END) AS total,
    MAX(CASE WHEN summary_type_text = 'TAX' THEN summary_value_text END) AS tax,
    MAX(CASE WHEN summary_type_text = 'SUBTOTAL' THEN summary_value_text END) AS subtotal,
    MAX(CASE WHEN summary_type_text = 'AMOUNT_DUE' THEN summary_value_text END) AS amount_due,
    MAX(CASE WHEN summary_type_text = 'AMOUNT_PAID' THEN summary_value_text END) AS amount_paid,
    MAX(CASE WHEN summary_type_text = 'PRIOR_BALANCE' THEN summary_value_text END) AS prior_balance,
    MAX(CASE WHEN summary_type_text = 'DISCOUNT' THEN summary_value_text END) AS discount,
    MAX(CASE WHEN summary_type_text = 'SHIPPING_HANDLING_CHARGE' THEN summary_value_text END) AS shipping_handling_charge
FROM
    ext1_invoice
GROUP BY
    in_invoice_processing_id, s3_object_key;