import json
import boto3

def lambda_handler(event, context):
    # Retrieve the S3 bucket name and object key from the event
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    object_key = event['Records'][0]['s3']['object']['key']
    
    # Initialize the Textract client
    textract_client = boto3.client('textract')
    
    # Invoke Textract's start_document_text_detection method on the uploaded PDF
    response = textract_client.start_document_text_detection(
        DocumentLocation={
            'S3Object': {
                'Bucket': bucket_name,
                'Name': object_key
            }
        }
    )
    
    # Wait for Textract to process the document and retrieve the JSON response
    job_id = response['JobId']
    textract_result = None
    while textract_result is None:
        response = textract_client.get_document_text_detection(JobId=job_id)
        status = response['JobStatus']
        if status == 'SUCCEEDED':
            textract_result = response
        elif status == 'FAILED':
            raise Exception('Textract processing failed')
    
    # Extract the JSON response from the Textract result
    json_response = json.dumps(textract_result['Blocks'])
    
    # Save the JSON response to the designated S3 bucket
    s3_client = boto3.client('s3')
    s3_client.put_object(
        Bucket='ccwebapp-textract-json',
        Key=f'{object_key.split("/")[-1]}.json',
        Body=json_response
    )
    
    return {
        'statusCode': 200,
        'body': json_response
    }
