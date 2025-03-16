-- Creates a table for storing raw JSON responses from Amazon Textract
-- alongside metadata about the source file and processing status,
-- serving as a staging area for further processing of invoice data.
CREATE TABLE in_invoice_processing (
    -- Unique identifier for each entry in the staging area
    id SERIAL PRIMARY KEY,
    
    -- The S3 object key where the source PDF/invoice is stored.
    -- This helps in tracking and referencing the original file.
    s3_object_key VARCHAR(255) NOT NULL,
    
    -- Raw JSON response from Amazon Textract as a JSONB object.
    -- JSONB format allows for efficient querying and manipulation of the JSON data.
    textract_json JSONB NOT NULL,
    
    -- Timestamp when the record was inserted into the database.
    -- Automatically captures the current timestamp at the time of insertion.
    received_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Unique constraint to prevent duplicate entries for the same S3 object key
    CONSTRAINT unique_s3_object_key UNIQUE (s3_object_key)
);

-- Optional: Add comments to the table and its columns for further clarification
COMMENT ON TABLE in_invoice_processing IS 'Staging area for raw JSON responses from Amazon Textract with metadata.';
COMMENT ON COLUMN in_invoice_processing.s3_object_key IS 'S3 object key for the source file.';
COMMENT ON COLUMN in_invoice_processing.textract_json IS 'Raw JSON response from Amazon Textract.';
COMMENT ON COLUMN in_invoice_processing.received_timestamp IS 'Timestamp when the record was inserted.';