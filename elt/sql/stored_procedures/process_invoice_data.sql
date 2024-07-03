CREATE OR REPLACE PROCEDURE refresh_and_insert_data()
LANGUAGE plpgsql
AS $$
BEGIN
    -- Refresh Invoice Views
    REFRESH MATERIALIZED VIEW ext1_invoice;
    REFRESH MATERIALIZED VIEW ext2_invoice;
    REFRESH MATERIALIZED VIEW for_invoice;
    REFRESH MATERIALIZED VIEW pro_invoice;

    -- Refresh Vendor Views
    REFRESH MATERIALIZED VIEW ext2_vendor;
    REFRESH MATERIALIZED VIEW for_vendor;
    REFRESH MATERIALIZED VIEW pro_vendor;

    -- Insert Invoice Records
    INSERT INTO out_invoice (
        in_invoice_processing_id,
        s3_object_key,
        upload_date,
        account_number,
        vendor_name,
        delivery_date,
        invoice_receipt_date,
        due_date,
        invoice_number,
        total,
        terms
    )
    SELECT
        in_invoice_processing_id,
        s3_object_key,
        upload_date,
        account_number,
        vendor_name,
        delivery_date,
        invoice_receipt_date,
        due_date,
        invoice_number,
        total,
        terms
    FROM 
        pro_invoice
    ON CONFLICT (invoice_number) DO NOTHING;

    -- Insert Vendor Records
    INSERT INTO out_vendor (
        vendor_id,
        vendor_name,
        vendor_address,
        vendor_city,
        vendor_state,
        vendor_zip,
        vendor_country,
        vendor_phone,
        vendor_email
    )
    SELECT
        vendor_id,
        vendor_name,
        vendor_address,
        vendor_city,
        vendor_state,
        vendor_zip,
        vendor_country,
        vendor_phone,
        vendor_email
    FROM 
        pro_vendor
    ON CONFLICT (vendor_id) DO NOTHING;

    -- Refresh Line Item Views
    REFRESH MATERIALIZED VIEW ext1_line_item;
    REFRESH MATERIALIZED VIEW ext2_line_item;
    REFRESH MATERIALIZED VIEW ext3_line_item;
    REFRESH MATERIALIZED VIEW for_line_item;
    REFRESH MATERIALIZED VIEW pro_line_item;

    -- Refresh Product View
    REFRESH MATERIALIZED VIEW pro_product;

    -- Insert Product Data into out_product Table
    INSERT INTO out_product (
        product_code,
        item_description,
        brand,
        unit_of_measure,
        most_recent_unit_price,
        most_recent_net_amount,
        most_recent_taxes,
        most_recent_discount,
        most_recent_quantity,
        most_recent_price,
        most_recent_pack,
        most_recent_size,
        most_recent_unit,
        most_recent_weight,
        last_updated
    )
    SELECT
        product_code,
        item_description,
        brand,
        unit_of_measure,
        most_recent_unit_price,
        most_recent_net_amount,
        most_recent_taxes,
        most_recent_discount,
        most_recent_quantity,
        most_recent_price,
        most_recent_pack,
        most_recent_size,
        most_recent_unit,
        most_recent_weight,
        last_updated
    FROM 
        pro_product
    ON CONFLICT (product_code, item_description) DO UPDATE SET
        brand = EXCLUDED.brand,
        unit_of_measure = EXCLUDED.unit_of_measure,
        most_recent_unit_price = EXCLUDED.most_recent_unit_price,
        most_recent_net_amount = EXCLUDED.most_recent_net_amount,
        most_recent_taxes = EXCLUDED.most_recent_taxes,
        most_recent_discount = EXCLUDED.most_recent_discount,
        most_recent_quantity = EXCLUDED.most_recent_quantity,
        most_recent_price = EXCLUDED.most_recent_price,
        most_recent_pack = EXCLUDED.most_recent_pack,
        most_recent_size = EXCLUDED.most_recent_size,
        most_recent_unit = EXCLUDED.unit,
        most_recent_weight = EXCLUDED.most_recent_weight,
        last_updated = EXCLUDED.last_updated;

    -- Refresh Final Line Item View
    REFRESH MATERIALIZED VIEW pro2_line_item;

    -- Insert Data into out_line_item Table
    INSERT INTO out_line_item (
        in_invoice_processing_id,
        s3_object_key,
        upload_date,
        invoice_id,
        invoice_receipt_id,
        expense_document_index,
        line_item_index,
        product_id, -- Now includes product_id
        product_code,
        brand,
        item_description,
        unit_price,
        net_amount,
        taxes,
        discount,
        quantity,
        price,
        unit_of_measure,
        pack,
        size,
        unit,
        weight,
        expense_row
    )
    SELECT
        in_invoice_processing_id,
        s3_object_key,
        upload_date,
        invoice_id,
        invoice_receipt_id,
        expense_document_index,
        line_item_index,
        product_id, -- Now includes product_id
        product_code,
        brand,
        item_description,
        unit_price,
        net_amount,
        taxes,
        discount,
        quantity,
        price,
        unit_of_measure,
        pack,
        size,
        unit,
        weight,
        expense_row
    FROM 
        pro2_line_item
    ON CONFLICT (line_item_id) DO UPDATE SET
        product_code = EXCLUDED.product_code,
        brand = EXCLUDED.brand,
        item_description = EXCLUDED.item_description,
        unit_price = EXCLUDED.unit_price,
        net_amount = EXCLUDED.net_amount​⬤