CREATE OR REPLACE VIEW for_invoice AS
SELECT 

 in_invoice_processing_id,
 s3_object_key,
 received_timestamp as upload_date,
 -- Customer Account Number
 COALESCE(account_number_label, account_number_hash, customer_number_label, customer_number_customer) as account_number,
 -- Vendor Name
 INITCAP(vendor_name) AS vendor_name,
  -- Delivery date (converting to MM/DD/YYYY format)
    TO_CHAR(
        COALESCE(
            TO_DATE(REGEXP_REPLACE(delivery_date_label, '^[A-Za-z]+, ', ''), 'MM/DD/YYYY'),
            TO_DATE(REGEXP_REPLACE(delivery_date_time, '^[A-Za-z]+, ', ''), 'MM/DD/YYYY')
        ), 
        'MM/DD/YYYY'
    ) AS delivery_date,
	
	 -- Invoice receipt date (converting to MM/DD/YYYY format)
    TO_CHAR(
        COALESCE(
            TO_DATE(REGEXP_REPLACE(invoice_receipt_date, '^[A-Za-z]+, ', ''), 'MM/DD/YYYY'),
            TO_DATE(REGEXP_REPLACE(invoice_receipt_date_upper, '^[A-Za-z]+, ', ''), 'MM/DD/YYYY'),
            TO_DATE(REGEXP_REPLACE(invoice_receipt_date_invoice, '^[A-Za-z]+, ', ''), 'MM/DD/YYYY'),
            TO_DATE(REGEXP_REPLACE(invoice_receipt_date_label, '^[A-Za-z]+, ', ''), 'MM/DD/YYYY'),
            TO_DATE(REGEXP_REPLACE(invoice_receipt_date_delv_period, '^[A-Za-z]+, ', ''), 'MM/DD/YYYY'),
            TO_DATE(REGEXP_REPLACE(invoice_receipt_date_delv, '^[A-Za-z]+, ', ''), 'MM/DD/YYYY'),
			TO_DATE(REGEXP_REPLACE(delivery_date_label, '^[A-Za-z]+, ', ''), 'MM/DD/YYYY'),
            TO_DATE(REGEXP_REPLACE(delivery_date_time, '^[A-Za-z]+, ', ''), 'MM/DD/YYYY')
        ), 
        'MM/DD/YYYY'
    ) AS invoice_date,
	
	-- Due date (converting to MM/DD/YYYY format)
    TO_CHAR(
        COALESCE(
            TO_DATE(REGEXP_REPLACE(due_date, '^[A-Za-z]+, ', ''), 'MM/DD/YYYY'),
            TO_DATE(REGEXP_REPLACE(due_date_due, '^[A-Za-z]+, ', ''), 'MM/DD/YYYY'),
            TO_DATE(REGEXP_REPLACE(due_date_label, '^[A-Za-z]+, ', ''), 'MM/DD/YYYY'),
            TO_DATE(REGEXP_REPLACE(due_date_payment, '^[A-Za-z]+, ', ''), 'MM/DD/YYYY')
        ), 
        'MM/DD/YYYY'
    ) AS due_date,
	
	-- Invoice receipt ID (removing hyphens and whitespace)
    REGEXP_REPLACE(
        COALESCE(
            invoice_receipt_id_number,
            invoice_receipt_id_invoice,
            invoice_receipt_id_label,
            invoice_receipt_id_number_upper
        ), 
        '[-\s]', '', 'g'
    ) AS invoice_number,
	
	 -- Total information (removing non-numeric characters and converting to DECIMAL)
    COALESCE(
        REGEXP_REPLACE(total, '[^\d.-]', '', 'g')::DECIMAL,
        REGEXP_REPLACE(total_pay_this_amount, '[^\d.-]', '', 'g')::DECIMAL,
        REGEXP_REPLACE(total_invoice, '[^\d.-]', '', 'g')::DECIMAL,
        REGEXP_REPLACE(total_totals, '[^\d.-]', '', 'g')::DECIMAL
    ) AS total,
	
	
	   -- Delivery date (storing as DATE)
    COALESCE(
        TO_DATE(REGEXP_REPLACE(delivery_date_label, '^[A-Za-z]+, ', ''), 'MM/DD/YYYY')::DATE,
        TO_DATE(REGEXP_REPLACE(delivery_date_time, '^[A-Za-z]+, ', ''), 'MM/DD/YYYY')::DATE
    ) AS delivery_date_date,

    -- Invoice receipt date (storing as DATE)
    COALESCE(
        TO_DATE(REGEXP_REPLACE(invoice_receipt_date, '^[A-Za-z]+, ', ''), 'MM/DD/YYYY')::DATE,
        TO_DATE(REGEXP_REPLACE(invoice_receipt_date_upper, '^[A-Za-z]+, ', ''), 'MM/DD/YYYY')::DATE,
        TO_DATE(REGEXP_REPLACE(invoice_receipt_date_invoice, '^[A-Za-z]+, ', ''), 'MM/DD/YYYY')::DATE,
        TO_DATE(REGEXP_REPLACE(invoice_receipt_date_label, '^[A-Za-z]+, ', ''), 'MM/DD/YYYY')::DATE,
        TO_DATE(REGEXP_REPLACE(invoice_receipt_date_delv_period, '^[A-Za-z]+, ', ''), 'MM/DD/YYYY')::DATE,
        TO_DATE(REGEXP_REPLACE(invoice_receipt_date_delv, '^[A-Za-z]+, ', ''), 'MM/DD/YYYY')::DATE,
        TO_DATE(REGEXP_REPLACE(delivery_date_label, '^[A-Za-z]+, ', ''), 'MM/DD/YYYY')::DATE,
        TO_DATE(REGEXP_REPLACE(delivery_date_time, '^[A-Za-z]+, ', ''), 'MM/DD/YYYY')::DATE
    ) AS invoice_date_date,

    -- Due date (storing as DATE)
    COALESCE(
        TO_DATE(REGEXP_REPLACE(due_date, '^[A-Za-z]+, ', ''), 'MM/DD/YYYY')::DATE,
        TO_DATE(REGEXP_REPLACE(due_date_due, '^[A-Za-z]+, ', ''), 'MM/DD/YYYY')::DATE,
        TO_DATE(REGEXP_REPLACE(due_date_label, '^[A-Za-z]+, ', ''), 'MM/DD/YYYY')::DATE,
        TO_DATE(REGEXP_REPLACE(due_date_payment, '^[A-Za-z]+, ', ''), 'MM/DD/YYYY')::DATE
    ) AS due_date_date
	


 FROM ext2_invoice
 