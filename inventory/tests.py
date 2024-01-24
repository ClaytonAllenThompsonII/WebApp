import datetime
import io
from unittest.mock import patch, MagicMock, ANY
import os
import tempfile  # Add this import
import uuid
from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone
from .forms import InventoryDataCollectionForm
from .models import InventoryItem
from .storage_backends import AWSStorageBackend




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


            # Create the SimpleUploadedFile mock object
            mock_image = SimpleUploadedFile(
                name='test.jpg',
                content=img_data,
                content_type='image/jpeg'
                )

            # Mock form data and files
            form_data = {
                'type': 'TestType',
                'image': mock_image, 
                'user': user.id # assign the user to the form data
            }

            # Set up files as a dictionary
            files = {'image':mock_image}

            # Test POST request to inventory view
            response = self.client.post('/inventory/', form_data, files=files)
            print("Response status code:", response.status_code)
            print("Response context:", response.context)

            # Assertions
            self.assertEqual(response.status_code, 200)

            # Ensure create_inventory_item was called once. Use ANY if you don't need to inspect arguments.
            mock_storage_backend.return_value.create_inventory_item.assert_called_once_with(ANY)

            # Inspect arguments passed to create_inventory_item, if necessary
            call_args, _ = mock_storage_backend.return_value.create_inventory_item.call_args
            print("Arguments passed to create_inventory_item:", call_args)

            # Ensure upload_file was called once with an instance of InMemoryUploadedFile
            mock_storage_backend.return_value.upload_file.assert_called_once()
            args, _ = mock_storage_backend.return_value.upload_file.call_args
            self.assertIsInstance(args[0], InMemoryUploadedFile)

            
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


class InventoryItemModelTest(TestCase):

    def test_inventory_item_model_creation(self):
    
        # Create a user for the ForeignKey relation
        User = get_user_model()
        user = User.objects.create_user(username='testuser', password='12345')

        # Create an InventoryItem instance
        item = InventoryItem(
            user=user,
            image='/Users/claytonthompson/Desktop/Source/WebApp/inventory_images/FishBinHotelPans.jpeg',
            type='TestType',
            filename='image.jpg'
        )

        # Save it to the database
        item.save()

        # Retrieve it back
        # pylint: disable=no-member
        retrieved_item = InventoryItem.objects.get(id=item.id)

        # Test assertions
        self.assertEqual(retrieved_item.user, user)
        self.assertEqual(retrieved_item.image, '/Users/claytonthompson/Desktop/Source/WebApp/inventory_images/FishBinHotelPans.jpeg')
        self.assertEqual(retrieved_item.type, 'TestType')
        self.assertEqual(retrieved_item.filename, 'image.jpg')
    

    def test_inventory_item_timestamp(self):
         # Create a user for the ForeignKey relation
        User = get_user_model()
        user = User.objects.create_user(username='testuser', password='12345')

        # Create an InventoryItem instance
        item = InventoryItem(
            user=user,
            image='/Users/claytonthompson/Desktop/Source/WebApp/inventory_images/FishBinHotelPans.jpeg',
            type='TestType',
            filename='image.jpg'
        )

        # Save it to the database
        item.save()

        # Retrieve it back
        # pylint: disable=no-member
        retrieved_item = InventoryItem.objects.get(id=item.id)

        # Check that the timestamp is recent
        now = timezone.now()
        time_diff = now - retrieved_item.timestamp
        self.assertTrue(time_diff < datetime.timedelta(seconds=5), "Timestamp is not within the expected time range")


        # Test assertions
        self.assertEqual(retrieved_item.user, user)
        self.assertEqual(retrieved_item.image, '/Users/claytonthompson/Desktop/Source/WebApp/inventory_images/FishBinHotelPans.jpeg')
        self.assertEqual(retrieved_item.type, 'TestType')
        self.assertEqual(retrieved_item.filename, 'image.jpg')


class InventoryDataCollectionFormTest(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='testuser', password='12345')

    def test_valid_data(self):
        # Sample data for a 1x1 black pixel in JPEG format
        image_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x03\x02\x02\x03\x02\x02\x03\x03\x03\x03\x04\x03\x03\x04\x05\x08\x05\x05\x04\x04\x05\n\x07\x07\x06\x08\x0c\n\x0c\x0c\x0b\n\x0b\x0b\r\x0e\x12\x10\r\x0e\x11\x0e\x0b\x0b\x10\x16\x10\x11\x13\x14\x15\x15\x15\x0c\x0f\x17\x18\x16\x14\x18\x12\x14\x15\x14\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\xff\xc4\x00\x14\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05\xff\xda\x00\x0c\x03\x01\x00\x02\x10\x03\x10\x00\x00\x01\xdf\x00\xff\xd9'

        form_data = {
            'type': 'TestType',
            'filename': 'test_image.jpg'
        }
        file_data = {
            'image': SimpleUploadedFile(name='test_image.jpg', content=image_data, content_type='image/jpeg')
        }
        form = InventoryDataCollectionForm(data=form_data, files=file_data)
        if not form.is_valid():
            print(form.errors)
        self.assertTrue(form.is_valid())

    def test_invalid_data(self):
         # Simulate uploading a non-image file (e.g., a Word document)
        form_data = {
            'user': self.user,
            'image': SimpleUploadedFile(name='document.docx', content=b'some document data', content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'),
            'type': 'TestType',
            'filename': 'document.docx'
        }
        form = InventoryDataCollectionForm(data=form_data, files={'image': form_data['image']})
        self.assertFalse(form.is_valid())

    def test_form_saves_data(self):

        # Create valid form data
        form_data = {
            'user': self.user,
            'image': SimpleUploadedFile(name='test_image.jpg', content=b'some image data', content_type='image/jpeg'),
            'type': 'TestType',
            'filename': 'test_image.jpg'
        }
        form = InventoryDataCollectionForm(data=form_data, files={'image': form_data['image']})
        if form.is_valid():
            inventory_item = form.save(commit=False)
            inventory_item.user = self.user
            inventory_item.save()

            # Retrieve the saved item and assert the data
            saved_item = InventoryItem.objects.get(id=inventory_item.id)
            self.assertEqual(saved_item.type, form_data['type'])
            self.assertEqual(saved_item.filename, form_data['filename'])
            self.assertEqual(saved_item.user, self.user)

