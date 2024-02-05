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
from .models import InventoryItem, GLLevel1, GLLevel2, GLLevel3, Product
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
            filename = storage.upload_file(mock_file, user_id='1')

            # Assertions
            self.assertTrue(filename.startswith('images/'))
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
                'gl_level_1_id': {'S': 'GL1ID123'},  # Example GL level 1 ID
                'gl_level_1_name': {'S': 'Food'},  # Example GL level 1 Name
                'gl_level_2_id': {'S': 'GL2ID456'},  # Example GL level 2 ID
                'gl_level_2_name': {'S': 'Meat'},  # Example GL level 2 Name
                'gl_level_3_id': {'S': 'GL3ID789'},  # Example GL level 3 ID
                'gl_level_3_name': {'S': 'Beef Short Rib'},  # Example GL level 3 Name
                'product_id': {'S': 'ProductID101'},  # Example Product ID
                'product_name': {'S': 'Beef Short Rib BNL'},  # Example Product Name
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
    """
    Test suite for the InventoryItem model.

    This class covers tests for the creation and timestamp validation of InventoryItem instances.
    It ensures that InventoryItem instances can be successfully created with all required fields,
    including relational fields to the user, GL levels, and products. Additionally, it verifies
    the auto-generated timestamp is accurate to the time of instance creation. The setUp method
    prepares the necessary database entities for testing, including a test user, hierarchical GL
    levels, a product associated with a GL level, and a dummy inventory item complete with an
    uploaded image.

    Tests included:
    - test_inventory_item_model_creation: Validates that InventoryItem instances are created
      accurately with all required relational fields and the filename.
    - test_inventory_item_timestamp: Checks the auto_now_add functionality of the timestamp field
      to ensure it reflects the creation time of the InventoryItem instance accurately.
    """

    def setUp(self):
        """
    Prepares the environment for inventory item model tests by creating necessary database
    entries. This includes a test user, General Ledger (GL) Level instances (1 to 3), a
    product instance tied to a GL Level 3, and a dummy inventory item with an image.
    """   
        # Create a user for ForeignKey relation to simulate an actual user environment.
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')

        # Initialize GL Level instances, each subsequent level referencing its parent.
        self.gl_level_1 = GLLevel1.objects.create(name="GL1 Test")
        self.gl_level_2 = GLLevel2.objects.create(name="GL2 Test", parent=self.gl_level_1)
        self.gl_level_3 = GLLevel3.objects.create(name="GL3 Test", parent=self.gl_level_2)

        # Create a Product instance, ensuring it's associated with a GL Level 3 instance.
        self.product = Product.objects.create(name="Product Test", parent=self.gl_level_3)

        # Prepare a dummy image file for testing image upload and storage.
        image_data = io.BytesIO(b"dummy image data")
        image_file = SimpleUploadedFile("test.jpg", image_data.getvalue())

        # Generate an InventoryItem instance to be used in various test scenarios.
        self.item = InventoryItem.objects.create(
            user=self.user,
            gl_level_1=self.gl_level_1,
            gl_level_2=self.gl_level_2,
            gl_level_3=self.gl_level_3,
            product=self.product,
            image=image_file,
            filename='image.jpg'
        )


    def test_inventory_item_model_creation(self):
        """
    Validates the successful creation and accurate field assignment of an InventoryItem instance.
    This test ensures that all relational fields (user, GL levels, and product) and the filename
    are correctly assigned. It also verifies the string representation (__str__) of the model.
    """
        # Retrieve the previously created inventory item for validation.
        # pylint: disable=no-member
        retrieved_item = InventoryItem.objects.get(id=self.item.id)

        # Test assertions
        # Assert each field matches the expected value set in the setUp method.
        self.assertEqual(retrieved_item.user, self.user)
        self.assertEqual(retrieved_item.gl_level_1, self.gl_level_1)
        self.assertEqual(retrieved_item.gl_level_2, self.gl_level_2)
        self.assertEqual(retrieved_item.gl_level_3, self.gl_level_3)
        self.assertEqual(retrieved_item.product, self.product)
        self.assertEqual(retrieved_item.filename, 'image.jpg')

        # Test __str__ method
        # Validate the string representation of the InventoryItem instance.
        expected_str = f'{self.user.username} - {self.product.name} ({self.item.timestamp})'
        self.assertEqual(str(retrieved_item), expected_str)

    def test_inventory_item_timestamp(self):
        """
    Verifies that the timestamp of the InventoryItem instance is within a reasonable range
    of the current time, ensuring the auto_now_add attribute functionality.
    """
        # Retrieve the inventory item to validate the timestamp.
        # pylint: disable=no-member
        retrieved_item = InventoryItem.objects.get(id=self.item.id)

        # Check that the timestamp is recent
        # Calculate the time difference between now and the item's timestamp.
        now = timezone.now()
        time_diff = now - retrieved_item.timestamp
        # Assert the timestamp is recent (within 5 seconds of the current time).
        self.assertTrue(time_diff < datetime.timedelta(seconds=5), "Timestamp is not within the expected time range")


class InventoryDataCollectionFormTest(TestCase):

    def setUp(self):
        """
    Initializes the test environment for InventoryDataCollectionForm tests by setting up
    necessary database entries and preparing form data.

    It creates a test user and instances for each GL level and a product, simulating a real-world
    scenario where form data would include selections for these entities. Additionally, it prepares
    a sample image file and form data to be used in various form validation tests.

    Attributes set:
    - self.user: A User instance for form submissions.
    - self.gl_level_1, self.gl_level_2, self.gl_level_3: Instances of GLLevel1, GLLevel2, and GLLevel3.
    - self.product: A Product instance linked to GLLevel3.
    - self.image_data: Binary data representing a 1x1 black pixel JPEG image.
    - self.form_data: A dictionary containing initial data for the form, including GL level IDs,
      product ID, and a filename for the image.
    - self.file_data: A dictionary containing the sample image file to simulate file upload in form submissions.
    """
        # Create user for associating with form submissions
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')

        # Create GL Levels and Product instances
        self.gl_level_1 = GLLevel1.objects.create(name="GL1 Name")
        self.gl_level_2 = GLLevel2.objects.create(name="GL2 Name", parent=self.gl_level_1)
        self.gl_level_3 = GLLevel3.objects.create(name="GL3 Name", parent=self.gl_level_2)
        self.product = Product.objects.create(name="Product Name", parent=self.gl_level_3)

        # Sample data for a 1x1 black pixel in JPEG format
        self.image_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x03\x02\x02\x03\x02\x02\x03\x03\x03\x03\x04\x03\x03\x04\x05\x08\x05\x05\x04\x04\x05\n\x07\x07\x06\x08\x0c\n\x0c\x0c\x0b\n\x0b\x0b\r\x0e\x12\x10\r\x0e\x11\x0e\x0b\x0b\x10\x16\x10\x11\x13\x14\x15\x15\x15\x0c\x0f\x17\x18\x16\x14\x18\x12\x14\x15\x14\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\xff\xc4\x00\x14\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05\xff\xda\x00\x0c\x03\x01\x00\x02\x10\x03\x10\x00\x00\x01\xdf\x00\xff\xd9'

        self.form_data = {
            'gl_level_1': self.gl_level_1.id,
            'gl_level_2': self.gl_level_2.id,
            'gl_level_3': self.gl_level_3.id,
            'product': self.product.id,
            'filename': 'test_file.jpg'
        }
        self.file_data = {
            'image': SimpleUploadedFile(name='test_image.jpg', content=self.image_data, content_type='image/jpeg')
        }

    def test_form_with_valid_data(self):
        
        form = InventoryDataCollectionForm(data=self.form_data, files=self.file_data)
        if not form.is_valid():
            print(form.errors)
        self.assertTrue(form.is_valid())

    def test_form_with_invalid_data(self):
        # Simulate uploading a non-image file (e.g., a Word document)
         # Modify the file data for an invalid test case, e.g., non-image file
        invalid_file_data = {
            'image': SimpleUploadedFile(name='document.docx', content=b'some document data', content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document')
        }
        form = InventoryDataCollectionForm(data=self.form_data, files=invalid_file_data)
        self.assertFalse(form.is_valid())

    def test_form_saves_data(self):

        # Create valid form data
        form = InventoryDataCollectionForm(data=self.form_data, files=self.file_data)
        if form.is_valid():
            item = form.save(commit=False)
            item.user = self.user
            item.save()

            # Retrieve the saved item and assert the data
            # Ensure you reference the saved `item` correctly
            saved_item = InventoryItem.objects.get(id=item.id)
            # Use self.form_data to access the test's form data
            # Adjust the assertions to match your model's fields
            self.assertEqual(saved_item.filename, self.form_data['filename'])
            self.assertEqual(saved_item.user, self.user)
            # Additional assertions can be made here based on the fields of InventoryItem
            # For example, if you want to check the GL levels and product:
            self.assertEqual(saved_item.gl_level_1.id, self.form_data['gl_level_1'])
            self.assertEqual(saved_item.gl_level_2.id, self.form_data['gl_level_2'])
            self.assertEqual(saved_item.gl_level_3.id, self.form_data['gl_level_3'])
            self.assertEqual(saved_item.product.id, self.form_data['product'])
        else:
            # If form is not valid, fail the test with form errors
            self.fail(f'Form did not validate: {form.errors}')

