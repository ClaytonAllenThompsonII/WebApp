import datetime
import io
from unittest.mock import patch, MagicMock, ANY
import os
import tempfile  # Add this import
import uuid
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from .forms import InventoryDataCollectionForm
from .storage_backends import AWSStorageBackend
# Import InMemoryUploadedFile from django.core.files.uploadedfile



# Create your tests here.
def fake_upload_file(file):
    """Simulate the upload_file method in AWSStorageBackend."""
    # Mimic the filename generation in the actual upload_file method
    return 'fakepath/test.jpg'


class AWSStorageBackendTest(TestCase):
    """Test suite for the AWSStorageBackend class."""

    @patch('boto3.client')
    def test_upload_file(self, mock_s3_client):
        """Test the upload_file method of AWSStorageBackend.
        Ensures that files are uploaded correctly and filenames are generated as expected."""
        with patch.dict(os.environ, {
            "S3_BUCKET_NAME": "test-bucket",
            "DYNAMODB_TABLE_NAME": "test-table",
            "AWS_DEFAULT_REGION": "us-east-1"  # Example region
            }):
            # Setup mock S3 client
            mock_s3_client.return_value.upload_fileobj.return_value = None

            # Create instance of your storage backend
            storage = AWSStorageBackend()

            # Mock file object
            mock_file = MagicMock(spec=io.BytesIO)
            mock_file.name = 'test.jpg'
            mock_file.read.return_value = b'file content'

            # Test upload_file method
            filename = storage.upload_file(mock_file)

            # Assertions
            self.assertTrue(filename.startswith('imagees/'))
            mock_s3_client.return_value.upload_fileobj.assert_called_with(mock_file, storage.bucket_name, filename)

    @patch('boto3.client')
    def test_create_inventory_item(self, mock_dynamodb_client):
        """Test the create_inventory_item method of AWSStorageBackend.
        Verifies that items are correctly created in the DynamoDB table."""
        with patch.dict(os.environ, {
            "S3_BUCKET_NAME": "test-bucket", 
            "DYNAMODB_TABLE_NAME": "test-table",
            "AWS_DEFAULT_REGION": "us-east-1"  # Example region
            }):
            # Setup mock DynamoDB client
            mock_dynamodb_client.return_value.put_item.return_value = None

            # Create instance of your storage backend
            storage = AWSStorageBackend()

            # Mock item data
            item_data = {
                'filename': {'S': 'test.jpg'},
                'label': {'S': 'TestLabel'},
                'timestamp': {'S': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
                'user_id': {'N': '1'}
            }

            # Test create_inventory_item method
            storage.create_inventory_item(item_data)

            # Assertions
            mock_dynamodb_client.return_value.put_item.assert_called_with(TableName=storage.table_name, Item=item_data)

class InventoryViewTest(TestCase):
    """Test suite for the inventory_view function."""

    @patch('inventory.views.AWSStorageBackend')
    def test_inventory_view(self, mock_storage_backend): # took out mock_upload_file,
        """Test the inventory_view function.
        Validates form handling, user authentication, and interaction with the AWSStorageBackend."""
        with patch.dict(os.environ, {
            "S3_BUCKET_NAME": "test-bucket",
            "DYNAMODB_TABLE_NAME": "test-table",
            "AWS_DEFAULT_REGION": "us-east-1"  # Example region
            }):

             # Setup mock storage backend return values
            mock_storage_backend.return_value.upload_file.return_value = 'fakepath/test.jpg'
            mock_storage_backend.return_value.create_inventory_item.return_value = None


            # Mock user
            user = User.objects.create_user('testuser', 'test@example.com', 'password')
            # Login
            self.client.login(username='testuser', password='password')

            # Read a real image file
            with open('/Users/claytonthompson/Desktop/Source/WebApp/inventory_images/FishBinHotelPans.jpeg', 'rb') as img_file:
                img_data = img_file.read()

            # Create a temporary file to store the image data
            temp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
            temp_file.write(img_data)
            temp_file.flush()

            # Create the SimpleUploadedFile mock object
            mock_image = SimpleUploadedFile(
                file=temp_file,  # Open temporary file for reading
                field_name='image',  # Name of the form field
                name='test.jpg',
                content_type='image/jpeg',
                size=len(img_data),  # Calculate size
                charset=None  # Assuming no specific charset
                    )

            # Remember to close and delete the temporary file after the test
            temp_file.close()
            temp_file.delete()

            # Mock form data and files
            form_data = {
                'type': 'TestType',
                'image': mock_image
            }

            # Set up files as a dictionary
            files = {'image':mock_image}

            # Test POST request to inventory view
            response = self.client.post('/inventory/', form_data, files=files)
            print("Response status code:", response.status_code)
            print("Response context:", response.context)

             # Assertions
            self.assertEqual(response.status_code, 200)
            # Fix 1: Ensure call order matches upload sequence
            mock_storage_backend.return_value.upload_file.assert_called_once_with(mock_image)
            mock_storage_backend.return_value.create_inventory_item.assert_called_once_with(ANY)

            # Fix 3: Inspect arguments passed to create_inventory_item
            call_args = mock_storage_backend.return_value.create_inventory_item.call_args
            print("Arguments passed to create_inventory_item:", call_args)
class DirectUploadFileTest(TestCase):
    @patch('inventory.storage_backends.AWSStorageBackend.__init__', return_value=None)
    @patch('inventory.storage_backends.AWSStorageBackend.upload_file', side_effect=fake_upload_file)
    @patch('boto3.client', return_value=MagicMock())  # Mock DynamoDB client

    def test_direct_upload_file(self, _mock_dynamo_client, mock_upload_file, _mock_storage_init):
        # Create an instance of AWSStorageBackend
        storage_backend = AWSStorageBackend()
        # Create a mock file
        mock_file = SimpleUploadedFile('test.jpg', b'file content', content_type='image/jpeg')
        # Directly call the upload_file method
        result = storage_backend.upload_file(mock_file)
        # Assert that the returned value is as expected
        self.assertEqual(result, 'fakepath/test.jpg')
        # Assert that the mock was called as expected
        mock_upload_file.assert_called_once_with(mock_file)
        