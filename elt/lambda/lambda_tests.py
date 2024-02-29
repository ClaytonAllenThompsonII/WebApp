"""
Unit tests for the AWS Lambda image preprocessing function.

This module contains unit tests for the Lambda function defined in image_preprocessor.py.
It uses the unittest framework for defining test cases and the unittest.mock library
for mocking AWS services and image processing functionalities.
"""
import unittest
from unittest.mock import patch, MagicMock
import image_preprocessor

class TestImagePreprocessorLambda(unittest.TestCase):

    @patch('image_preprocessor.s3_client')
    @patch('image_preprocessor.Image')
    def test_lambda_handler(self, mock_image, mock_s3_client):
        # Mock S3 event data
        event = {
            'Records': [
                {
                    's3': {
                        'bucket': {
                            'name': 'source-bucket'
                        },
                        'object': {
                            'key': 'test.jpg'
                        }
                    }
                }
            ]
        }
        context = None  # Context is often not needed for basic testing

        # Mock for s3_client.download_file
        mock_s3_client.download_file.side_effect = lambda bucket, key, file: file.write(b'test data')

        # Mock for s3_client.upload_file
        mock_s3_client.upload_file.side_effect = MagicMock()

        # Mock for Image.open and resize
        mock_image_open = mock_image.open.return_value.__enter__.return_value
        mock_image_open.resize.return_value = mock_image_open

        # Call the lambda_handler function
        image_preprocessor.lambda_handler(event, context)

        # Assertions to verify expected behavior
        mock_s3_client.download_file.assert_called_with('source-bucket', 'test.jpg', ANY)
        mock_s3_client.upload_file.assert_called_with(ANY, 'your-resized-image-bucket', 'test.jpg')
        mock_image_open.resize.assert_called_with((1280, 720))

if __name__ == '__main__':
    unittest.main()
