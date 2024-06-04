CREATE OR REPLACE VIEW ext2_invoice AS

SELECT
    in_invoice_processing_id,
    s3_object_key,
    MAX(received_timestamp) AS received_timestamp,
    
    -- Vendor information
    MAX(CASE WHEN summary_type_text = 'ACCOUNT_NUMBER' AND summary_label_text = 'Account Number:' THEN summary_value_text ELSE NULL END) AS account_number_label,
    MAX(CASE WHEN summary_type_text = 'ACCOUNT_NUMBER' AND summary_label_text = 'ACCOUNT#' THEN summary_value_text ELSE NULL END) AS account_number_hash,
	
	-- Customer information
    MAX(CASE WHEN summary_type_text = 'CUSTOMER_NUMBER' AND summary_label_text = 'Customer #' THEN summary_value_text ELSE NULL END) AS customer_number_label,
    MAX(CASE WHEN summary_type_text = 'CUSTOMER_NUMBER' AND summary_label_text = 'CUSTOMER' THEN summary_value_text ELSE NULL END) AS customer_number_customer,

      -- Name information
    MAX(CASE WHEN summary_type_text = 'NAME' AND summary_label_text = 'CUSTOMER:' THEN summary_value_text ELSE NULL END) AS name_customer,
    MAX(CASE WHEN summary_type_text = 'NAME' AND summary_label_text = 'Printed Name:' THEN summary_value_text ELSE NULL END) AS name_printed,
    MAX(CASE WHEN summary_type_text = 'NAME' AND summary_label_text IS NULL THEN summary_value_text ELSE NULL END) AS name_null,

    -- Vendor name
    MAX(CASE WHEN summary_type_text = 'VENDOR_NAME' AND summary_label_text IS NULL THEN summary_value_text ELSE NULL END) AS vendor_name,


      -- Delivery date information
    MAX(CASE WHEN summary_type_text = 'DELIVERY_DATE' AND summary_label_text = 'Delivery Date:' THEN summary_value_text ELSE NULL END) AS delivery_date_label,
    MAX(CASE WHEN summary_type_text = 'DELIVERY_DATE' AND summary_label_text = 'DELIVERY DATE/TIME' THEN summary_value_text ELSE NULL END) AS delivery_date_time,

    -- Invoice receipt date information
    MAX(CASE WHEN summary_type_text = 'INVOICE_RECEIPT_DATE' AND summary_label_text = 'Date' THEN summary_value_text ELSE NULL END) AS invoice_receipt_date,
    MAX(CASE WHEN summary_type_text = 'INVOICE_RECEIPT_DATE' AND summary_label_text = 'DATE' THEN summary_value_text ELSE NULL END) AS invoice_receipt_date_upper,
    MAX(CASE WHEN summary_type_text = 'INVOICE_RECEIPT_DATE' AND summary_label_text = 'INVOICE DATE' THEN summary_value_text ELSE NULL END) AS invoice_receipt_date_invoice,
    MAX(CASE WHEN summary_type_text = 'INVOICE_RECEIPT_DATE' AND summary_label_text = 'Invoice Date:' THEN summary_value_text ELSE NULL END) AS invoice_receipt_date_label,
    MAX(CASE WHEN summary_type_text = 'INVOICE_RECEIPT_DATE' AND summary_label_text = 'DELV. DATE' THEN summary_value_text ELSE NULL END) AS invoice_receipt_date_delv_period,
    MAX(CASE WHEN summary_type_text = 'INVOICE_RECEIPT_DATE' AND summary_label_text = 'DELV DATE' THEN summary_value_text ELSE NULL END) AS invoice_receipt_date_delv,

 -- Due date information
    MAX(CASE WHEN summary_type_text = 'DUE_DATE' AND summary_label_text = 'Due Date' THEN summary_value_text ELSE NULL END) AS due_date,
    MAX(CASE WHEN summary_type_text = 'DUE_DATE' AND summary_label_text = 'Date Due:' THEN summary_value_text ELSE NULL END) AS due_date_due,
    MAX(CASE WHEN summary_type_text = 'DUE_DATE' AND summary_label_text = 'Due Date:' THEN summary_value_text ELSE NULL END) AS due_date_label,
    MAX(CASE WHEN summary_type_text = 'DUE_DATE' AND summary_label_text = 'PAYMENT DUE DATE' THEN summary_value_text ELSE NULL END) AS due_date_payment,

    -- Invoice receipt ID information
    MAX(CASE WHEN summary_type_text = 'INVOICE_RECEIPT_ID' AND summary_label_text = 'Invoice #' THEN summary_value_text ELSE NULL END) AS invoice_receipt_id_number,
    MAX(CASE WHEN summary_type_text = 'INVOICE_RECEIPT_ID' AND summary_label_text = 'INVOICE' THEN summary_value_text ELSE NULL END) AS invoice_receipt_id_invoice,
    MAX(CASE WHEN summary_type_text = 'INVOICE_RECEIPT_ID' AND summary_label_text = 'Invoice Number:' THEN summary_value_text ELSE NULL END) AS invoice_receipt_id_label,
    MAX(CASE WHEN summary_type_text = 'INVOICE_RECEIPT_ID' AND summary_label_text = 'INVOICE NUMBER' THEN summary_value_text ELSE NULL END) AS invoice_receipt_id_number_upper,

      -- Payment terms information
    MAX(CASE WHEN summary_type_text = 'PAYMENT_TERMS' AND summary_label_text = 'Terms' THEN summary_value_text ELSE NULL END) AS payment_terms,
    MAX(CASE WHEN summary_type_text = 'PAYMENT_TERMS' AND summary_label_text = 'PAYMENT TERMS:' THEN summary_value_text ELSE NULL END) AS payment_terms_colon,
    MAX(CASE WHEN summary_type_text = 'PAYMENT_TERMS' AND summary_label_text = 'TERMS' THEN summary_value_text ELSE NULL END) AS terms_upper,

    -- PO number information
    MAX(CASE WHEN summary_type_text = 'PO_NUMBER' AND summary_label_text = 'PURCHASE ORDER' THEN summary_value_text ELSE NULL END) AS po_number_purchase_order,
    MAX(CASE WHEN summary_type_text = 'PO_NUMBER' AND summary_label_text = 'P-O- #' THEN summary_value_text ELSE NULL END) AS po_number_po_hash,
    MAX(CASE WHEN summary_type_text = 'PO_NUMBER' AND summary_label_text = 'PO NUMBER' THEN summary_value_text ELSE NULL END) AS po_number_po_number,
    MAX(CASE WHEN summary_type_text = 'PO_NUMBER' AND summary_label_text = 'P.O. Number:' THEN summary_value_text ELSE NULL END) AS po_number_po_label,

        -- Service charge information
    MAX(CASE WHEN summary_type_text = 'SERVICE_CHARGE' AND summary_label_text = 'MISC CHARGES CHGS FOR FUEL SURCHARGE' THEN summary_value_text ELSE NULL END) AS service_charge_fuel_surcharge,

    -- Subtotal information
    MAX(CASE WHEN summary_type_text = 'SUBTOTAL' AND summary_label_text = '02-COOLER' THEN summary_value_text ELSE NULL END) AS subtotal_02_cooler,
    MAX(CASE WHEN summary_type_text = 'SUBTOTAL' AND summary_label_text = '01-DRY GOODS' THEN summary_value_text ELSE NULL END) AS subtotal_01_dry_goods,
    MAX(CASE WHEN summary_type_text = 'SUBTOTAL' AND summary_label_text = 'TOTAL' THEN summary_value_text ELSE NULL END) AS subtotal_total,
    MAX(CASE WHEN summary_type_text = 'SUBTOTAL' AND summary_label_text = 'SUB TOTAL FOR: 01-DRY GOODS' THEN summary_value_text ELSE NULL END) AS subtotal_sub_total_01_dry_goods,
    MAX(CASE WHEN summary_type_text = 'SUBTOTAL' AND summary_label_text = '03-FREEZER' THEN summary_value_text ELSE NULL END) AS subtotal_03_freezer,
    MAX(CASE WHEN summary_type_text = 'SUBTOTAL' AND summary_label_text = 'TOTAL GROSS AMT' THEN summary_value_text ELSE NULL END) AS subtotal_total_gross_amt,
    MAX(CASE WHEN summary_type_text = 'SUBTOTAL' AND summary_label_text = 'SUB TOTAL FOR: 03-FREEZER' THEN summary_value_text ELSE NULL END) AS subtotal_sub_total_03_freezer,
    MAX(CASE WHEN summary_type_text = 'SUBTOTAL' AND summary_label_text = 'TOTAL NET AMOUNT' THEN summary_value_text ELSE NULL END) AS subtotal_total_net_amount,
    MAX(CASE WHEN summary_type_text = 'SUBTOTAL' AND summary_label_text = 'GROUP TOTAL***' THEN summary_value_text ELSE NULL END) AS subtotal_group_total_3_stars,
    MAX(CASE WHEN summary_type_text = 'SUBTOTAL' AND summary_label_text = 'GROUP TOTAL**' THEN summary_value_text ELSE NULL END) AS subtotal_group_total_2_stars,
    MAX(CASE WHEN summary_type_text = 'SUBTOTAL' AND summary_label_text = 'GROUP TOTAL****' THEN summary_value_text ELSE NULL END) AS subtotal_group_total_4_stars,
    MAX(CASE WHEN summary_type_text = 'SUBTOTAL' AND summary_label_text = 'GROUP TOTAL*' THEN summary_value_text ELSE NULL END) AS subtotal_group_total_1_star,
    MAX(CASE WHEN summary_type_text = 'SUBTOTAL' AND summary_label_text = 'GROUP TOTAL' THEN summary_value_text ELSE NULL END) AS subtotal_group_total,

    -- Tax information
    MAX(CASE WHEN summary_type_text = 'TAX' AND summary_label_text = 'TOTAL TAXES' THEN summary_value_text ELSE NULL END) AS tax_total_taxes,
    MAX(CASE WHEN summary_type_text = 'TAX' AND summary_label_text = 'Tax' THEN summary_value_text ELSE NULL END) AS tax,
    MAX(CASE WHEN summary_type_text = 'TAX' AND summary_label_text = 'Tax Rt' THEN summary_value_text ELSE NULL END) AS tax_rt,
    MAX(CASE WHEN summary_type_text = 'TAX' AND summary_label_text = 'TAX' THEN summary_value_text ELSE NULL END) AS tax_upper,

    -- Taxpayer ID information
    MAX(CASE WHEN summary_type_text = 'TAX_PAYER_ID' AND summary_label_text = 'Tax ID' THEN summary_value_text ELSE NULL END) AS taxpayer_id,

    -- Total information
    MAX(CASE WHEN summary_type_text = 'TOTAL' AND summary_label_text = 'Total' THEN summary_value_text ELSE NULL END) AS total,
    MAX(CASE WHEN summary_type_text = 'TOTAL' AND summary_label_text = 'Due' THEN summary_value_text ELSE NULL END) AS total_due,
    MAX(CASE WHEN summary_type_text = 'TOTAL' AND summary_label_text = 'SUB TOTAL FOR:' THEN summary_value_text ELSE NULL END) AS total_sub_total_for,
    MAX(CASE WHEN summary_type_text = 'TOTAL' AND summary_label_text = 'PAY THIS AMOUNT' THEN summary_value_text ELSE NULL END) AS total_pay_this_amount,
    MAX(CASE WHEN summary_type_text = 'TOTAL' AND summary_label_text = 'INVOICE TOTAL' THEN summary_value_text ELSE NULL END) AS total_invoice,
    MAX(CASE WHEN summary_type_text = 'TOTAL' AND summary_label_text = 'OnAcct' THEN summary_value_text ELSE NULL END) AS total_on_acct,
    MAX(CASE WHEN summary_type_text = 'TOTAL' AND summary_label_text = 'Totals' THEN summary_value_text ELSE NULL END) AS total_totals,

    -- Discount information
    MAX(CASE WHEN summary_type_text = 'DISCOUNT' AND summary_label_text = 'TOTAL DISCOUNTS' THEN summary_value_text ELSE NULL END) AS discount_total_discounts,
    MAX(CASE WHEN summary_type_text = 'DISCOUNT' AND summary_label_text = 'TOTAL DEPOSIT FEE' THEN summary_value_text ELSE NULL END) AS discount_total_deposit_fee,

    -- Other information
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'BPC:' THEN summary_value_text ELSE NULL END) AS other_bpc,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'NOTE:' THEN summary_value_text ELSE NULL END) AS other_note,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'SIZE:' THEN summary_value_text ELSE NULL END) AS other_size,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'ITEM#:' THEN summary_value_text ELSE NULL END) AS other_item_number,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'TOT WT:' THEN summary_value_text ELSE NULL END) AS other_total_weight,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'Stop #' THEN summary_value_text ELSE NULL END) AS other_stop_number,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'VIA:' THEN summary_value_text ELSE NULL END) AS other_via,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'Rep' THEN summary_value_text ELSE NULL END) AS other_rep,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'WD#' THEN summary_value_text ELSE NULL END) AS other_wd_number,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'Route #' THEN summary_value_text ELSE NULL END) AS other_route_number,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'All goods received in good order by authorized receiving agent:' THEN summary_value_text ELSE NULL END) AS other_goods_received,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'Driver:' THEN summary_value_text ELSE NULL END) AS other_driver,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'Delivery Time:' THEN summary_value_text ELSE NULL END) AS other_delivery_time,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'Sales Representative' THEN summary_value_text ELSE NULL END) AS other_sales_representative,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'Via' THEN summary_value_text ELSE NULL END) AS other_via_lower,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'H.A.C.C.P. CERTIFICATON #' THEN summary_value_text ELSE NULL END) AS other_haccp_certification_number,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'Page Count=' THEN summary_value_text ELSE NULL END) AS other_page_count_equals,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'P.O Box' THEN summary_value_text ELSE NULL END) AS other_po_box,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'Page Count:' THEN summary_value_text ELSE NULL END) AS other_page_count,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'P.O. BOX' THEN summary_value_text ELSE NULL END) AS other_po_box_upper,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'PERMIT' THEN summary_value_text ELSE NULL END) AS other_permit,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'Customer Notes:' THEN summary_value_text ELSE NULL END) AS other_customer_notes,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'Page' THEN summary_value_text ELSE NULL END) AS other_page,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'T/WT=' THEN summary_value_text ELSE NULL END) AS other_twt_equals,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'H.A.C.C.P. CERTIFICATON' THEN summary_value_text ELSE NULL END) AS other_haccp_certification,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'TOTAL BOTTLES' THEN summary_value_text ELSE NULL END) AS other_total_bottles,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'Route #:' THEN summary_value_text ELSE NULL END) AS other_route_number_colon,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'SUB TOTAL FOR:' THEN summary_value_text ELSE NULL END) AS other_sub_total_for,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'TERMS AND CONDITIONS' THEN summary_value_text ELSE NULL END) AS other_terms_and_conditions,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'DEX' THEN summary_value_text ELSE NULL END) AS other_dex,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'SIGNATURE:' THEN summary_value_text ELSE NULL END) AS other_signature,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'Registration' THEN summary_value_text ELSE NULL END) AS other_registration,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'License#' THEN summary_value_text ELSE NULL END) AS other_license_number,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'SEAFOOD LICENSE' THEN summary_value_text ELSE NULL END) AS other_seafood_license,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'Delivered By:' THEN summary_value_text ELSE NULL END) AS other_delivered_by,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'TERMS' THEN summary_value_text ELSE NULL END) AS other_terms,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'Stop #:' THEN summary_value_text ELSE NULL END) AS other_stop_number_colon,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'PERMIT EXP' THEN summary_value_text ELSE NULL END) AS other_permit_exp,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'MANIFEST#' THEN summary_value_text ELSE NULL END) AS other_manifest_number,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'Total Received By:' THEN summary_value_text ELSE NULL END) AS other_total_received_by,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'TOTAL CS/ BTLS' THEN summary_value_text ELSE NULL END) AS other_total_cs_btls,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'DRIVER:' THEN summary_value_text ELSE NULL END) AS other_driver_colon,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'PAGE' THEN summary_value_text ELSE NULL END) AS other_page_upper,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'MA:' THEN summary_value_text ELSE NULL END) AS other_ma,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'IMPORTANT' THEN summary_value_text ELSE NULL END) AS other_important,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'ROUTE' THEN summary_value_text ELSE NULL END) AS other_route,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'CLOSE:' THEN summary_value_text ELSE NULL END) AS other_close,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'CASES' THEN summary_value_text ELSE NULL END) AS other_cases,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'H.A.C.C.P. CERTIFICATION #' THEN summary_value_text ELSE NULL END) AS other_haccp_certification_number_upper,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'CUBE GROSS WT.' THEN summary_value_text ELSE NULL END) AS other_cube_gross_weight,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'ORDER SUMMARY :' THEN summary_value_text ELSE NULL END) AS other_order_summary,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'TRUCK STOP' THEN summary_value_text ELSE NULL END) AS other_truck_stop,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'CUST SIGNED INVOICE EVIDENCES or ALL ITEMS SIGN' THEN summary_value_text ELSE NULL END) AS other_cust_signed_invoice,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'GROUP TOTAL****' THEN summary_value_text ELSE NULL END) AS other_group_total_4_stars,
    MAX(CASE WHEN summary_type_text = 'OTHER' AND summary_label_text = 'SPLIT TOT.PCS' THEN summary_value_text ELSE NULL END) AS other_split_tot_pcs,

      -- Extracting other details as JSONB with COALESCE to avoid null keys/values
    jsonb_object_agg(
        COALESCE(CASE WHEN summary_type_text = 'OTHER' THEN summary_label_text ELSE NULL END, 'unknown'),
        COALESCE(CASE WHEN summary_type_text = 'OTHER' THEN summary_value_text ELSE NULL END, 'unknown')
    ) FILTER (WHERE summary_type_text = 'OTHER' AND summary_value_text IS NOT NULL) AS other_details




FROM
    ext1_invoice
GROUP BY
    in_invoice_processing_id, s3_object_key;