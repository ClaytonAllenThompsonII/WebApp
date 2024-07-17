# WebApp

## Data Engineering 

### ELT / Lambda / SRC 

## process_invoice_pdf Lambda Function

### Overview
The `process_invoice_pdf` Lambda function handles the processing of uploaded invoice PDFs, leveraging AWS Textract to extract data and generate JSON responses. This function is crucial for transforming raw invoice PDFs into structured JSON data for further analysis.

### Functionality

1. **Initialization**:
   - Sets up the S3 client and retrieves the bucket names from environment variables.
   - Lists all objects (invoices) in Folder-A of the invoice bucket.

2. **Processing Each Invoice**:
   - **Move PDF from Folder-A to Folder-B**: The function copies the PDF file from Folder-A to Folder-B and then deletes the original PDF in Folder-A.
   - **Invoke Textract**: The function invokes AWS Textract’s `start_expense_analysis` on the uploaded PDF in Folder-B.
   - **Wait for Textract Analysis**: The function waits for the Textract analysis to complete by repeatedly polling the Textract service with exponential backoff.
   - **Store JSON Response**: Once the Textract analysis is complete, the JSON response is extracted and stored in Folder-A of the textract bucket.
   - **Move PDF from Folder-B to Folder-C**: Finally, the PDF is copied from Folder-B to Folder-C, and the original PDF in Folder-B is deleted.

## load_json_pg Lambda Function

### Overview
The `load_json_pg` Lambda function is designed to transfer JSON files from an S3 bucket to a PostgreSQL database. This function plays a crucial role in moving processed invoice data (stored as JSON files) into a relational database for further analysis and reporting.

### Functionality

1. **Initialization**:
   - The function initializes an S3 client.
   - Environment variables are used to retrieve bucket names for S3 operations.
   - A connection to the PostgreSQL RDS instance is established.

2. **Processing Workflow**:
   - **Move JSON Files**:
     - JSON files are moved from Folder-A to Folder-B in the S3 bucket.
   - **Process and Load JSON Files**:
     - JSON files from Folder-B are processed in batches and loaded into the PostgreSQL database.
   - **Move Processed Files**:
     - After processing, JSON files are moved from Folder-B to Folder-C.