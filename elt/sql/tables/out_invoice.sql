
CREATE TABLE invoice (
  invoice_id SERIAL PRIMARY KEY,               -- Auto-incrementing Invoice ID as primary key
  invoice_receipt_id VARCHAR(255) NOT NULL,    -- Vendor assigned invoice number, typically unique per vendor
  account_number VARCHAR(255),                 -- Account number for the invoice, linked to a customer or business account
  tax_payer_id VARCHAR(255),                   -- Tax payer identification number for the entity being invoiced
  customer_number VARCHAR(255),                -- Unique identifier for the customer to whom the invoice is issued
  vendor_id INT,                               -- Foreign key linking to the vendor table, identifies the vendor issuing the invoice
  order_date DATE,                             -- Date on which the order related to the invoice was placed
  due_date DATE,                               -- Date by which the payment for the invoice is due
  delivery_date DATE,                          -- Date on which the goods or services were delivered
  invoice_receipt_date DATE,                   -- Date when the invoice was issued/received
  po_number VARCHAR(255),                      -- Purchase order number associated with the invoice
  payment_terms VARCHAR(255),                  -- Payment terms agreed upon, e.g., Net 30, due on receipt
  total DECIMAL,                               -- Total amount of the invoice including taxes and fees
  amount_due DECIMAL,                          -- Amount currently due on the invoice
  amount_paid DECIMAL,                         -- Amount already paid towards the invoice
  subtotal DECIMAL,                            -- Subtotal of the invoice before taxes and additional charges
  tax DECIMAL,                                 -- Tax amount charged on the invoice
  service_charge DECIMAL,                      -- Service charges, if any, applied on the invoice
  prior_balance DECIMAL,                       -- Any prior balance that was carried forward onto this invoice
  discount DECIMAL,                            -- Discounts applied to the invoice
  shipping_handling_charge DECIMAL,            -- Charges for shipping and handling included in the invoice
  FOREIGN KEY (vendor_id) REFERENCES vendor(vendor_id) ON DELETE SET NULL  -- Ensures integrity of reference to vendor table, sets to NULL if referenced vendor is deleted
);
