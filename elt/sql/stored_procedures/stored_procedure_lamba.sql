CREATE OR REPLACE PROCEDURE insert_vendor_invoice_product_line_item_data()
LANGUAGE plpgsql
AS $$
BEGIN
    -- Step 1: Refresh the pro_vendor view to get the latest vendor data
    PERFORM
    'SELECT 1 FROM pro_vendor LIMIT 1';

    -- Step 2: Insert or update vendor data in the out_vendor table
    INSERT INTO out_vendor (
        most_recent_in_invoice_processing_id,
        most_recent_s3_object_key,
        most_recent_upload_date,
        account_number,
        vendor_name,
        vendor_phone,
        vendor_address,
        vendor_street,
        vendor_city,
        vendor_state,
        vendor_zip_code,
        address_block,
        vendor_remit_address,
        remit_to_street,
        remit_to_city,
        remit_to_state,
        remit_to_zip_code,
        remit_to_address_block,
        inserted_at,
        batched_at
    )
    SELECT 
        most_recent_in_invoice_processing_id,
        most_recent_s3_object_key,
        most_recent_upload_date,
        account_number,
        vendor_name,
        vendor_phone,
        vendor_address,
        vendor_street,
        vendor_city,
        vendor_state,
        vendor_zip_code,
        address_block,
        vendor_remit_address,
        remit_to_street,
        remit_to_city,
        remit_to_state,
        remit_to_zip_code,
        remit_to_address_block,
        CURRENT_TIMESTAMP,
        NULL 
    FROM 
        pro_vendor
    ON CONFLICT (vendor_name, account_number)
    DO UPDATE SET
        most_recent_in_invoice_processing_id = EXCLUDED.most_recent_in_invoice_processing_id,
        most_recent_s3_object_key = EXCLUDED.most_recent_s3_object_key,
        most_recent_upload_date = EXCLUDED.most_recent_upload_date,
        vendor_address = EXCLUDED.vendor_address,
        vendor_street = EXCLUDED.vendor_street,
        vendor_city = EXCLUDED.vendor_city,
        vendor_state = EXCLUDED.vendor_state,
        vendor_zip_code = EXCLUDED.vendor_zip_code,
        address_block = EXCLUDED.address_block,
        vendor_remit_address = EXCLUDED.vendor_remit_address,
        remit_to_street = EXCLUDED.remit_to_street,
        remit_to_city = EXCLUDED.remit_to_city,
        remit_to_state = EXCLUDED.remit_to_state,
        remit_to_zip_code = EXCLUDED.remit_to_zip_code,
        remit_to_address_block = EXCLUDED.remit_to_address_block,
        inserted_at = EXCLUDED.inserted_at,
        batched_at = COALESCE(out_vendor.batched_at, EXCLUDED.batched_at);

    -- Step 3: Refresh the pro_invoice view to get the latest invoice data
    PERFORM
    'SELECT 1 FROM pro_invoice LIMIT 1';

    -- Step 4: Insert or update invoice data in the out_invoice table
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
      vendor_id,
      inserted_at,
      batched_at
    )
    SELECT 
      pi.in_invoice_processing_id,
      pi.s3_object_key,
      pi.upload_date,
      pi.account_number,
      pi.vendor_name,
      pi.delivery_date,
      pi.invoice_receipt_date,
      pi.due_date,
      pi.invoice_number,
      pi.total,
      ov.vendor_id,
      CURRENT_TIMESTAMP,
      NULL
    FROM pro_invoice pi
    LEFT JOIN out_vendor ov 
      ON pi.account_number = ov.account_number
      AND pi.vendor_name = ov.vendor_name
    ON CONFLICT (invoice_number)
    DO UPDATE SET
      in_invoice_processing_id = EXCLUDED.in_invoice_processing_id,
      s3_object_key = EXCLUDED.s3_object_key,
      upload_date = EXCLUDED.upload_date,
      account_number = EXCLUDED.account_number,
      vendor_name = EXCLUDED.vendor_name,
      delivery_date = EXCLUDED.delivery_date,
      invoice_receipt_date = EXCLUDED.invoice_receipt_date,
      due_date = EXCLUDED.due_date,
      total = EXCLUDED.total,
      vendor_id = EXCLUDED.vendor_id,
      inserted_at = EXCLUDED.inserted_at;

    -- Step 5: Refresh the pro_product view to get the latest product data
    PERFORM
    'SELECT 1 FROM pro_product LIMIT 1';

    -- Step 6: Insert or update product data in the out_product table
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
        most_recent_unit = EXCLUDED.most_recent_unit,
        most_recent_weight = EXCLUDED.most_recent_weight,
        last_updated = EXCLUDED.last_updated;

    -- Step 7: Refresh the pro2_line_item view to get the latest line item data
    PERFORM
    'SELECT 1 FROM pro2_line_item LIMIT 1';

    -- Step 8: Insert or update line item data in the out_line_item table
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
        expense_row,
        gl3_id, -- New field
        gl3_name -- New field
    )
    SELECT
        pli.in_invoice_processing_id,
        pli.s3_object_key,
        pli.upload_date,
        i.invoice_id,
        pli.invoice_receipt_id,
        pli.expense_document_index,
        pli.line_item_index,
        p.product_id, -- Now includes product_id
        pli.product_code,
        pli.brand,
        pli.item_description,
        pli.unit_price,
        pli.net_amount,
        pli.taxes,
        pli.discount,
        pli.quantity,
        pli.price,
        pli.unit_of_measure,
        pli.pack,
        pli.size,
        pli.unit,
        pli.weight,
        pli.expense_row,
        NULL, -- Initial value for gl3_id
        NULL  -- Initial value for gl3_name
    FROM 
        pro2_line_item pli
    JOIN 
        out_invoice i
    ON 
        pli.invoice_receipt_id = i.invoice_number
    JOIN 
        out_product p
    ON 
        pli.product_code = p.product_code
    AND 
        pli.item_description = p.item_description
    ON CONFLICT (line_item_id) DO UPDATE SET
        product_code = EXCLUDED.product_code,
        brand = EXCLUDED.brand,
        item_description = EXCLUDED.item_description,
        unit_price = EXCLUDED.unit_price,
        net_amount = EXCLUDED.net_amount,
        taxes = EXCLUDED.taxes,
        discount = EXCLUDED.discount,
        quantity = EXCLUDED.quantity,
        price = EXCLUDED.price,
        unit_of_measure = EXCLUDED.unit_of_measure,
        pack = EXCLUDED.pack,
        size = EXCLUDED.size,
        unit = EXCLUDED.unit,
        weight = EXCLUDED.weight,
        expense_row = EXCLUDED.expense_row,
        product_id = EXCLUDED.product_id,
        gl3_id = EXCLUDED.gl3_id,
        gl3_name = EXCLUDED.gl3_name;
END;
$$;