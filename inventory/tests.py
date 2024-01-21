import datetime
import io
from unittest.mock import patch, MagicMock
import os

from django.test import TestCase
from django.contrib.auth.models import User
from .forms import InventoryDataCollectionForm
from .storage_backends import AWSStorageBackend



# Create your tests here.

class AWSStorageBackendTest(TestCase):
    """Test suite for the AWSStorageBackend class."""

    @patch('boto3.client')
    def test_upload_file(self, mock_s3_client):
        """Test the upload_file method of AWSStorageBackend.
        Ensures that files are uploaded correctly and filenames are generated as expected."""
        with patch.dict(os.environ, {"S3_BUCKET_NAME": "test-bucket", "DYNAMODB_TABLE_NAME": "test-table"}):
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
        with patch.dict(os.environ, {"S3_BUCKET_NAME": "test-bucket", "DYNAMODB_TABLE_NAME": "test-table"}):
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

    @patch('inventory.storage_backends.AWSStorageBackend.upload_file')
    @patch('inventory.storage_backends.AWSStorageBackend.create_inventory_item')

    def test_inventory_view(self, mock_upload_file, mock_create_inventory_item):
        """Test the inventory_view function.
        Validates form handling, user authentication, and interaction with the AWSStorageBackend."""
        with patch.dict(os.environ, {"S3_BUCKET_NAME": "test-bucket", "DYNAMODB_TABLE_NAME": "test-table"}):
            # Mock user
            user = User.objects.create_user('testuser', 'test@example.com', 'password')

            # Login
            self.client.login(username='testuser', password='password')

            # Mock form data
            form_data = {
                'type': 'TestType',
                'image': MagicMock(),
                'timestamp': datetime.datetime.now(),
                'user': user.id
            }

            # Test POST request to inventory view
            response = self.client.post('/inventory/', form_data)

            # Assertions
            self.assertEqual(response.status_code, 200)
            mock_upload_file.assert_called_once()
            mock_create_inventory_item.assert_called_once()
