# WebApp
Django Web Application for inventory and invoice management.

## Image Classification with 🤗 Hugging Face

### Overview
This section of the application provides functionality to classify images using a fine-tuned Vision Transformer (ViT) model from Hugging Face. The model is specifically trained on the `nateraw/food101` dataset, which is used to accurately identify and classify food-related images. 

### View Functions

#### `image_classification_view(request)`

This is the primary view that handles image classification requests. It processes image uploads and interacts with the Hugging Face API to return classification results.

- **POST Request Handling**:
  - **Form Validation**: When a POST request is made, the view first validates the image upload form (`ImageUploadForm`). If valid, it processes the image.
  - **Image Processing**:
    - The uploaded image is temporarily saved to the file system using Django’s `default_storage`. 
    - The saved image is then reopened to reset the file pointer, ensuring it is ready for processing.
  - **API Request**: The image is sent to the Hugging Face API using the `query_huggingface()` function. The function processes the image and returns classification results.
  - **JSON Response**: The classification results are returned as a JSON response, which includes labels and confidence scores for each identified category.

- **GET Request Handling**:
  - If a GET request is made, the view simply renders the image upload form, allowing users to upload images for classification.

#### `query_huggingface(image_file)`

This function is responsible for sending the image file to the Hugging Face API for classification.

- **File Preparation**: 
  - The file pointer is reset to ensure the image file is read from the beginning. 
  - The image file content is read as bytes, which is necessary for sending it as a binary payload to the API.

- **API Request**:
  - A POST request is made to the Hugging Face API with the image data.
  - The request includes the necessary headers, such as the authorization token (`HF_API_KEY`) and the image data.

- **Response Handling**:
  - The function checks for any HTTP errors and logs the full response content.
  - If successful, the JSON response from the API is parsed and logged for debugging purposes.
  - The parsed result, which includes labels and their respective confidence scores, is returned to the calling function.

- **Error Handling**:
  - The function catches and logs any HTTP errors or request exceptions that occur during the API call.
  - If an error occurs, it returns a JSON response with an error message, indicating the nature of the failure.

### Dependencies
- **Hugging Face API**: The classification feature relies on the Hugging Face Inference API, particularly the Vision Transformer (ViT) model pre-trained on the ImageNet-21k dataset and fine-tuned on the `food101` dataset.
- **Django Storage**: The view utilizes Django’s `default_storage` system for temporarily saving and handling uploaded images before sending them to the API.



## OpenAI API Integration

This section of the application integrates with OpenAI's GPT models to automate the generation of product names and enhance product descriptions. The following functions utilize the OpenAI API to perform these tasks based on data retrieved from the database.

### Generate Product Name

#### `generate_product_name(request)`

This function generates a concise and appealing product name using the OpenAI API. It takes the following steps:

- **Request Handling**:
  - **POST Request**: The function expects a POST request with a `product_id` in the body.
  - **Error Handling**: If the `product_id` is not provided or the product is not found, the function returns an error response.

- **Data Retrieval**:
  - The function fetches the product details from the database using the provided `product_id`.
  - It also retrieves related line item information, such as `GL3 Name` and `Expense Row`, if available.

- **Prompt Generation**:
  - The function constructs a prompt that includes the product’s description, brand, and any additional available information (e.g., GL3 Name, Expense Row).
  - The prompt instructs the OpenAI model to generate a product name that is short, concise, and clearly descriptive.

- **OpenAI API Call**:
  - The function calls the OpenAI API with the constructed prompt, using the GPT-4 model.
  - The generated product name is extracted from the API response and returned as a JSON response.

### Enhance Product Details

#### `enhance_product_details(request)`

This function enhances product details by generating a more comprehensive description using the OpenAI API. The process involves:

- **Request Handling**:
  - **POST Request**: The function expects a POST request with a `product_id` in the body.
  - **Error Handling**: If the `product_id` is missing or the product is not found, the function returns an error response.

- **Data Retrieval**:
  - The function retrieves the product and associated line items from the database.
  - It compiles additional details such as `Item Descriptions`, `Expense Rows`, and `GL3 Names` from the line items.

- **Prompt Generation**:
  - A prompt is created to instruct the OpenAI model to generate an enhanced product description.
  - The prompt includes various details like item descriptions, expense rows, and GL3 names, focusing on clarity and conciseness.
  - The prompt also asks the model to estimate the product's expiration range based on its characteristics.

- **OpenAI API Call**:
  - The function calls the OpenAI API with the generated prompt, using the GPT-4 model.
  - The enhanced product details are extracted from the API response and returned as a JSON response.




## Amazone Web Services (AWS)

## Machine Learning API (AWS Textract)

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


## Data Engineering, ELT 

## load_json_pg Lambda Function

### Overview
The `load_json_pg` Lambda function is designed to transfer JSON files from an S3 bucket to a RDS PostgreSQL database. This function plays a crucial role in moving processed invoice data (stored as JSON files) into a relational database for further analysis and reporting.

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