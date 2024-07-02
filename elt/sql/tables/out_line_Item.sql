-- Step 1: Create the line_item table with an invoice_id column
CREATE TABLE out_line_item (
    line_item_id SERIAL PRIMARY KEY, -- Primary key
    in_invoice_processing_id INT,
    s3_object_key TEXT,
    upload_date TIMESTAMP,
    invoice_id INT, -- Foreign key to the out_invoice table
    invoice_receipt_id TEXT,
    expense_document_index INT,
    line_item_index INT,
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
    CONSTRAINT fk_invoice FOREIGN KEY (invoice_id) REFERENCES out_invoice(invoice_id) -- Foreign key constraint
);