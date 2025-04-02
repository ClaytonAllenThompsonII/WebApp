-- Create the out_line_item_processed table
CREATE TABLE out_line_item_processed (
    line_item_id INT PRIMARY KEY, -- Primary key
    in_invoice_processing_id INT,
    s3_object_key TEXT,
    upload_date TIMESTAMP,
    invoice_id INT,
    invoice_receipt_id TEXT,
    expense_document_index INT,
    line_item_index INT,
    product_id INT,
    product_code TEXT,
    brand TEXT,
    item_description TEXT,
    unit_price NUMERIC,
    net_amount NUMERIC,
    taxes NUMERIC,
    discount NUMERIC,
    quantity NUMERIC,
    price NUMERIC,
    unit_of_measure TEXT,
    pack NUMERIC,
    size NUMERIC,
    unit TEXT,
    weight NUMERIC,
    expense_row TEXT,
    gl3_id INT;
    

);


-- local testing using pg admin
psql -h localhost -U your_username -d your_database -c 

-- update this file and fields. 
\copy out_line_item_processed(line_item_id, in_invoice_processing_id, s3_object_key, upload_date, invoice_id, invoice_receipt_id, expense_document_index, line_item_index, product_id, product_code, brand, item_description, unit_price, net_amount, taxes, discount, quantity, price, unit_of_measure, pack, size, unit, weight, expense_row, gl3_id) FROM '/Users/claytonthompson/Desktop/out_line_item.csv' DELIMITER ',' CSV HEADER NULL AS 'NULL';
