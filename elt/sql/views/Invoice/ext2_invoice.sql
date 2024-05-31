CREATE OR REPLACE VIEW ext2_invoice AS

SELECT
    in_invoice_processing_id,
    s3_object_key,
    MAX(received_timestamp) AS received_timestamp,
    
    -- Vendor information
    MAX(CASE WHEN summary_type_text = 'ACCOUNT_NUMBER' THEN summary_value_text END) AS account_number,
    MAX(CASE WHEN summary_type_text = 'CUSTOMER_NUMBER' THEN summary_value_text END) AS customer_number,

    MAX(CASE WHEN summary_type_text = 'TAX_PAYER_ID' THEN summary_value_text END) AS taxpayer_id,

    
    MAX(CASE WHEN summary_type_text = 'VENDOR_NAME' THEN summary_value_text END) AS vendor_name,
    
    -- Temporal data
    MAX(CASE WHEN summary_type_text = 'ORDER_DATE' THEN summary_value_text END) AS order_date,
    MAX(CASE WHEN summary_type_text = 'INVOICE_RECEIPT_ID' THEN summary_value_text END) AS invoice_receipt_id,
    MAX(CASE WHEN summary_type_text = 'INVOICE_RECEIPT_DATE' THEN summary_value_text END) AS invoice_receipt_date,
    MAX(CASE WHEN summary_type_text = 'DUE_DATE' THEN summary_value_text END) AS due_date,
    MAX(CASE WHEN summary_type_text = 'DELIVERY_DATE' THEN summary_value_text END) AS delivery_date,
    MAX(CASE WHEN summary_type_text = 'PO_NUMBER' THEN summary_value_text END) AS po_number,
    
    -- Payment terms variations
    MAX(CASE WHEN summary_type_text = 'PAYMENT_TERMS' THEN summary_value_text END) AS payment_terms,
    MAX(CASE WHEN summary_type_text = 'PAYMENT_TERMS' AND summary_label_text = 'Terms' THEN summary_value_text END) AS terms,
    MAX(CASE WHEN summary_type_text = 'PAYMENT_TERMS' AND summary_label_text = 'PAYMENT TERMS:' THEN summary_value_text END) AS payment_terms_colon,
    MAX(CASE WHEN summary_type_text = 'PAYMENT_TERMS' AND summary_label_text = 'TERMS' THEN summary_value_text END) AS terms_upper,
    
    -- Financial data
    --Totals
    MAX(CASE WHEN summary_type_text = 'TOTAL' THEN summary_value_text END) AS invoice_total,
    MAX(CASE WHEN summary_type_text = 'TOTAL' AND summary_label_text = 'PAY THIS AMOUNT' THEN summary_value_text END) AS pay_this_amount,
    MAX(CASE WHEN summary_type_text = 'TOTAL' AND summary_label_text = 'Total' THEN summary_value_text END) AS Total,
    MAX(CASE WHEN summary_type_text = 'TOTAL' AND summary_label_text = 'INVOICE TOTAL' THEN summary_value_text END) AS invoice_total_2,
    MAX(CASE WHEN summary_type_text = 'TOTAL' AND summary_label_text = 'Due' THEN summary_value_text END) AS due_amount,
    MAX(CASE WHEN summary_type_text = 'TAX' THEN summary_value_text END) AS tax,
    MAX(CASE WHEN summary_type_text = 'SUBTOTAL' AND summary_label_text = 'TOTAL GROSS AMT' THEN summary_value_text END) AS total_gross_amount,
    MAX(CASE WHEN summary_type_text = 'SUBTOTAL' AND summary_label_text = 'TOTAL NET AMOUNT' THEN summary_value_text END) AS total_net_amount,
    MAX(CASE WHEN summary_type_text = 'AMOUNT_DUE' THEN summary_value_text END) AS amount_due,
    MAX(CASE WHEN summary_type_text = 'AMOUNT_PAID' THEN summary_value_text END) AS amount_paid,
    MAX(CASE WHEN summary_type_text = 'PRIOR_BALANCE' THEN summary_value_text END) AS prior_balance,
    MAX(CASE WHEN summary_type_text = 'DISCOUNT' THEN summary_value_text END) AS discount,
    MAX(CASE WHEN summary_type_text = 'SERVICE_CHARGE' THEN summary_value_text END) AS service_charge,
    
    -- Catch-all field for less frequent TOTAL labels with COALESCE to avoid null keys/values
    jsonb_object_agg(
        COALESCE(CASE WHEN summary_type_text = 'TOTAL' AND summary_label_text NOT IN ('PAY THIS AMOUNT', 'Total', 'INVOICE TOTAL', 'Due') THEN summary_label_text ELSE NULL END, 'unknown'),
        COALESCE(CASE WHEN summary_type_text = 'TOTAL' AND summary_label_text NOT IN ('PAY THIS AMOUNT', 'Total', 'INVOICE TOTAL', 'Due') THEN summary_value_text ELSE NULL END, 'unknown')
    ) FILTER (WHERE summary_type_text = 'TOTAL' AND summary_value_text IS NOT NULL) AS other_total_details,

    -- Extracting other details as JSONB with COALESCE to avoid null keys/values
    jsonb_object_agg(
        COALESCE(CASE WHEN summary_type_text = 'OTHER' THEN summary_label_text ELSE NULL END, 'unknown'),
        COALESCE(CASE WHEN summary_type_text = 'OTHER' THEN summary_value_text ELSE NULL END, 'unknown')
    ) FILTER (WHERE summary_type_text = 'OTHER' AND summary_value_text IS NOT NULL) AS other_details

FROM
    ext1_invoice
GROUP BY
    in_invoice_processing_id, s3_object_key;