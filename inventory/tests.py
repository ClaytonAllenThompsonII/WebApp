import datetime
import io
from unittest.mock import patch, MagicMock, ANY
import os
import tempfile  # Add this import
import uuid
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.utils import timezone
from django.urls import reverse
from botocore.exceptions import ClientError
from .forms import InventoryQueueItemForm
from .models import InventoryQueueItem, InventoryCollectionCycle, GLLevel1, GLLevel2, GLLevel3
from invoice.models import ProcessedProduct  # Assuming ProcessedProduct is the replacement for Product
from .storage_backends import AWSStorageBackend


# Create your tests here.
def fake_upload_file(file, user_id, group_id, cycle_id):
    """Simulate the upload_file method in AWSStorageBackend."""
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
    """Tests the inventory_view function with detailed print statements."""
    def setUp(self):
        """
        Prepares the test environment before each test method is run. This includes creating a test user, 
        GL level and product instances, and preparing a dummy image file for upload.

        - A test user is created for simulating authenticated sessions.
        - GL Level instances (1 through 3) and a product instance are created to simulate database entries
        that would be selected through the form in a real-world scenario.
        - A byte string representing a dummy image file is prepared for testing file uploads.
        """
        print('Setting up test environment for InventoryViewTest.')
        # User setup for authenticated sessions
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        # GL level and product setup for form selections
        self.gl_level_1 = GLLevel1.objects.create(name="GL1")
        self.gl_level_2 = GLLevel2.objects.create(name="GL2", parent=self.gl_level_1)
        self.gl_level_3 = GLLevel3.objects.create(name="GL3", parent=self.gl_level_2)
        self.product = Product.objects.create(name="Product", parent=self.gl_level_3)

        # Dummy image file setup for upload testing
        self.image_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x03\x02\x02\x03\x02\x02\x03\x03\x03\x03\x04\x03\x03\x04\x05\x08\x05\x05\x04\x04\x05\n\x07\x07\x06\x08\x0c\n\x0c\x0c\x0b\n\x0b\x0b\r\x0e\x12\x10\r\x0e\x11\x0e\x0b\x0b\x10\x16\x10\x11\x13\x14\x15\x15\x15\x0c\x0f\x17\x18\x16\x14\x18\x12\x14\x15\x14\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\xff\xc4\x00\x14\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05\xff\xda\x00\x0c\x03\x01\x00\x02\x10\x03\x10\x00\x00\x01\xdf\x00\xff\xd9'
        self.image_file = SimpleUploadedFile(name='test_image.jpg', content=self.image_data, content_type='image/jpeg')
        print('Test environment setup complete.')

    @patch('inventory.views.AWSStorageBackend')
    def test_inventory_view_post_request(self, mock_storage_backend):
            """
            Tests the POST request handling of the inventory_view function. This method simulates a form submission
            with valid data and checks the interaction with the AWSStorageBackend for file upload and metadata storage.

            The method uses patching to mock the AWSStorageBackend, avoiding real AWS interactions during the test.
            It asserts the correct behavior of the inventory_view function when receiving a POST request, including:
            - Form validation and submission.
            - Interaction with AWSStorageBackend for file uploads.
            - Correct response status code.
            """
            print('Testing inventory_view POST request functionality.')
            # Mock setup for AWS interactions
            mock_storage_backend.return_value.upload_file.return_value = 'uploaded/test_image.jpg'
            mock_storage_backend.return_value.create_inventory_item.return_value = None

            # Prepare form submission
            post_data = {
                'gl_level_1': str(self.gl_level_1.id),
                'gl_level_2': str(self.gl_level_2.id),
                'gl_level_3': str(self.gl_level_3.id),
                'product': str(self.product.id)
            }
    
            # Prepare files separately
            files = {'image': self.image_file}

            response = self.client.post('/inventory/', data=post_data, files=files)
            print(f'POST request to inventory_view made with status code {response.status_code}.')

            # Add this to print form errors if the form is invalid
            if response.context and 'form' in response.context:
                form = response.context['form']
                if not form.is_valid():
                    print("Form errors", form.errors.as_text())

            # Assertions
            mock_storage_backend.assert_called_once()
            print('AWSStorageBackend mocked methods called as expected.')
            self.assertEqual(response.status_code, 200)
            print('inventory_view POST request test completed successfully.')

    def test_inventory_view_GET(self):
            """
            Test that the inventory view returns a 200 response and uses the correct template 
            for GET requests. This test ensures the view is accessible by authenticated users 
            and renders the expected template with the correct context.
            """
            print('Testing inventory_view GET request functionality.')
            # Perform a GET request to the inventory view
            response = self.client.get('/inventory/')  # Update URL as necessary
            print(f'GET request to inventory_view made with status code {response.status_code}.')

            # Assertions
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'inventory/training_data.html')  # Ensure this matches your template path
            print('inventory_view GET request test asserts correct status code and template usage.')

    def test_inventory_view_redirect_if_not_logged_in(self):
        """
        Test that the inventory view redirects to the login page if the user is not logged in. 
        This test confirms the view's authentication protection by ensuring unauthenticated 
        users cannot access the inventory submission form and are redirected appropriately.
        """
        print('Testing inventory_view redirect for unauthenticated access.')
        # Log out any session that might be active to simulate unauthenticated access
        self.client.logout()

        # Attempt to access the inventory view
        response = self.client.get('/inventory/')  # Update URL as necessary

        # Assertions
        self.assertNotEqual(response.status_code, 200)
        expected_login_url = '/login/?next=/inventory/'  # Updated to reflect your login URL and the next parameter
        self.assertTrue(response.url.startswith(expected_login_url))
        print(f'Unauthenticated GET request to inventory_view redirected to {response.url}.')
               
class DirectUploadFileTest(TestCase):
    @patch('inventory.storage_backends.AWSStorageBackend.__init__', return_value=None)
    @patch('inventory.storage_backends.AWSStorageBackend.upload_file', side_effect=fake_upload_file)
    def test_direct_upload_file(self, mock_upload_file, _mock_storage_init):
        # Create an instance of AWSStorageBackend
        storage_backend = AWSStorageBackend()
        # Create a mock file
        mock_file = SimpleUploadedFile('test.jpg', b'file content', content_type='image/jpeg')
        # Directly call the upload_file method with required parameters
        result = storage_backend.upload_file(mock_file, user_id='1', group_id='1', cycle_id='1')
        # Assert that the returned value is as expected
        self.assertEqual(result, 'fakepath/test.jpg')
        # Assert that the mock was called with the expected parameters
        mock_upload_file.assert_called_once_with(mock_file, '1', '1', '1')


class InventoryQueueItemModelTest(TestCase):
    """
    Test suite for the InventoryQueueItem model.

    This class covers tests for the creation and timestamp validation of InventoryQueueItem instances.
    It ensures that InventoryQueueItem instances can be successfully created with all required fields,
    including relational fields to the user, GL levels, product, and the inventory cycle. Additionally,
    it verifies the auto-generated timestamp is accurate to the time of instance creation.

    Tests included:
    - test_inventory_queue_item_model_creation: Validates that InventoryQueueItem instances are created
      accurately with all required relational fields and the filename.
    - test_inventory_queue_item_timestamp: Checks that the auto_now_add attribute on the timestamp
      field reflects the creation time accurately.
    """

    def setUp(self):
        """
        Prepares the environment for InventoryQueueItem model tests by creating necessary database entries.
        This includes creating a test user, hierarchical GL levels, a ProcessedProduct instance tied to GL Level 3,
        an InventoryCollectionCycle instance, and a dummy InventoryQueueItem with an image.
        """
        # Create a user for ForeignKey relation
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')

        # Create GL Level instances (hierarchy: GLLevel1 -> GLLevel2 -> GLLevel3)
        self.gl_level_1 = GLLevel1.objects.create(name="GL1 Test")
        self.gl_level_2 = GLLevel2.objects.create(name="GL2 Test", parent=self.gl_level_1)
        self.gl_level_3 = GLLevel3.objects.create(name="GL3 Test", parent=self.gl_level_2)

        # Create a ProcessedProduct instance for association
        self.product = ProcessedProduct.objects.create(
            product_id=1,
            product_code="P001",
            item_description="Test Product Description",
            brand="Test Brand"
        )

        # Create an InventoryCollectionCycle instance (required for InventoryQueueItem)
        self.active_cycle = InventoryCollectionCycle.objects.create(user=self.user)

        # Prepare a dummy image file for testing image upload and storage.
        image_data = io.BytesIO(b"dummy image data")
        image_file = SimpleUploadedFile("test.jpg", image_data.getvalue())

        # Create an InventoryQueueItem instance.
        # Note: Set product_name explicitly so that __str__ is predictable.
        self.queue_item = InventoryQueueItem.objects.create(
            user=self.user,
            gl_level_1=self.gl_level_1,
            gl_level_2=self.gl_level_2,
            gl_level_3=self.gl_level_3,
            product=self.product,
            product_name=self.product.item_description,  # Use the product's description for display
            filename='s3_key_placeholder.jpg',  # Simulated S3 key
            size=12.34,
            unit='kg',
            inventory_cycle=self.active_cycle,
            # If you still store a local image, you could include it here:
            image=image_file
        )

    def test_inventory_queue_item_model_creation(self):
        """
        Validates the successful creation and accurate field assignment of an InventoryQueueItem instance.
        Ensures that all relational fields (user, GL levels, product, and inventory cycle) and the filename
        are correctly assigned. Also verifies the string representation (__str__) of the model.
        """
        retrieved_item = InventoryQueueItem.objects.get(id=self.queue_item.id)

        self.assertEqual(retrieved_item.user, self.user)
        self.assertEqual(retrieved_item.gl_level_1, self.gl_level_1)
        self.assertEqual(retrieved_item.gl_level_2, self.gl_level_2)
        self.assertEqual(retrieved_item.gl_level_3, self.gl_level_3)
        self.assertEqual(retrieved_item.product, self.product)
        self.assertEqual(retrieved_item.filename, 's3_key_placeholder.jpg')
        self.assertEqual(retrieved_item.size, 12.34)
        self.assertEqual(retrieved_item.unit, 'kg')
        self.assertEqual(retrieved_item.inventory_cycle, self.active_cycle)

        # Expected string uses product_name (or "No Product" if not set) and the timestamp.
        expected_str = f'{self.user.username} - {self.product.item_description} ({retrieved_item.timestamp})'
        self.assertEqual(str(retrieved_item), expected_str)

    def test_inventory_queue_item_timestamp(self):
        """
        Verifies that the timestamp of the InventoryQueueItem instance is within a reasonable range
        of the current time, ensuring that auto_now_add on the timestamp field is functioning properly.
        """
        retrieved_item = InventoryQueueItem.objects.get(id=self.queue_item.id)
        now = timezone.now()
        time_diff = now - retrieved_item.timestamp
        # Check that the timestamp is recent (within 5 seconds)
        self.assertTrue(time_diff < datetime.timedelta(seconds=5), "Timestamp is not within the expected time range")
class InventoryQueueItemFormTest(TestCase):
    """
    Provides a suite of tests for the InventoryQueueItemForm to ensure it accurately
    validates data, handles invalid inputs appropriately, and successfully saves valid
    data to the database.

    The setUp method prepares a comprehensive test environment by creating essential
    database records such as a User, General Ledger (GL) levels, and a ProcessedProduct.
    It also sets up both valid and invalid form and file data to simulate various user submission
    scenarios.

    Tests included:
    - test_form_with_valid_data: Verifies that the InventoryQueueItemForm correctly validates
      when provided with valid data and a valid image file.
    - test_form_with_invalid_data: Checks the form's response to invalid data (e.g., non-image file),
      ensuring robust data validation.
    - test_form_saves_data: Confirms that upon submission of valid data, the form correctly
      creates an InventoryQueueItem instance with the provided details.
    """

    def setUp(self):
        """
        Initializes the test environment for InventoryQueueItemForm tests by setting up
        necessary database entries and preparing form data.

        It creates a test user, GL level instances (GLLevel1, GLLevel2, GLLevel3), and a ProcessedProduct,
        simulating a real-world scenario where form data includes selections for these entities.
        Additionally, it prepares sample image file data and form data to be used in form validation tests.
        """
        # Create user for form submissions
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')

        # Create GL Level instances
        self.gl_level_1 = GLLevel1.objects.create(name="GL1 Name")
        self.gl_level_2 = GLLevel2.objects.create(name="GL2 Name", parent=self.gl_level_1)
        self.gl_level_3 = GLLevel3.objects.create(name="GL3 Name", parent=self.gl_level_2)

        # Create a ProcessedProduct instance (assumed replacement for the old Product model)
        self.product = ProcessedProduct.objects.create(
            product_id=1,
            product_code="P001",
            item_description="Product Description",
            brand="BrandX"
        )
        
        # For the form, only include fields that are in InventoryQueueItemForm (product, size, unit)
        self.form_data = {
            'product': self.product.id,
            'size': '10.5',
            'unit': 'kg'
        }
        # Prepare sample image file data for file upload tests.
        self.file_data = {
            'image': SimpleUploadedFile(
                name='test_image.jpg',
                content=b'\xff\xd8\xff\xe0\x00\x10JFIF',
                content_type='image/jpeg'
            )
        }

    def test_form_with_valid_data(self):
        """
        Verifies that the InventoryQueueItemForm correctly validates when provided
        with valid data and a valid image file.
        """
        form = InventoryQueueItemForm(data=self.form_data, files=self.file_data)
        if not form.is_valid():
            print(form.errors)
        self.assertTrue(form.is_valid())

    def test_form_with_invalid_data(self):
        """
        Tests that the InventoryQueueItemForm correctly rejects invalid file uploads.
        Specifically, this test attempts to upload a non-image file (e.g., a Word document)
        and asserts that the form is invalid.
        """
        invalid_file_data = {
            'image': SimpleUploadedFile(
                name='document.docx',
                content=b'some document data',
                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
        }
        form = InventoryQueueItemForm(data=self.form_data, files=invalid_file_data)
        self.assertFalse(form.is_valid())

    def test_form_saves_data(self):
        """
        Tests that InventoryQueueItemForm correctly saves data to the database upon
        submission of valid data. This test creates a form instance with valid data and file,
        then saves the form (using commit=False) to obtain a model instance. It manually sets
        additional required fields (such as user and filename) and saves the instance.
        Finally, it retrieves the saved instance from the database to verify that all attributes
        match the input data.
        """
        form = InventoryQueueItemForm(data=self.form_data, files=self.file_data)
        if form.is_valid():
            # Save without committing to the database so we can add extra fields
            item = form.save(commit=False)
            item.user = self.user
            # In our workflow, the image is uploaded to S3 and its key is stored in filename.
            # For testing, we simulate this with a placeholder.
            item.filename = 's3_key_placeholder.jpg'
            # Additional fields such as GL levels could be set here if needed.
            item.save()

            saved_item = InventoryQueueItem.objects.get(id=item.id)
            self.assertEqual(saved_item.filename, 's3_key_placeholder.jpg')
            self.assertEqual(saved_item.user, self.user)
            self.assertEqual(saved_item.product.id, self.product.id)
            self.assertEqual(str(saved_item.size), "10.5")
            self.assertEqual(saved_item.unit, "kg")
        else:
            self.fail(f'Form did not validate: {form.errors}')





@override_settings(MEDIA_ROOT='/tmp/django_test')
class FileUploadTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.gl_level_1 = GLLevel1.objects.create(name="Test GL Level 1")
        self.gl_level_2 = GLLevel2.objects.create(name="Test GL Level 2", parent=self.gl_level_1)
        self.gl_level_3 = GLLevel3.objects.create(name="Test GL Level 3", parent=self.gl_level_2)
        self.product = Product.objects.create(name="Test Product", parent=self.gl_level_3)

    @patch('inventory.views.AWSStorageBackend.upload_file', side_effect=ClientError({}, "operation_name"))
    def test_upload_file_error(self, mock_upload):
        # Log in the test user
        self.client.login(username='testuser', password='testpassword')

        # Prepare a dummy file (consider using an actual small image file here)
        with open('/Users/claytonthompson/Desktop/Source/WebApp/inventory_images/FishBinHotelPans.jpeg', 'rb') as img:
            dummy_file = SimpleUploadedFile('test_file.jpg', img.read(), content_type='image/jpeg')

        # Prepare POST data including the required fields
        post_data = {
            'image': dummy_file,
            'gl_level_1': self.gl_level_1.id,
            'gl_level_2': self.gl_level_2.id,
            'gl_level_3': self.gl_level_3.id,
            'product': self.product.id,
        }

        response = self.client.post(reverse('inventory_app'), post_data, follow=True)

        # Check that the user was redirected correctly
        self.assertEqual(response.status_code, 200)
        print(response.request['PATH_INFO'])
        self.assertTrue('/inventory/' in response.request['PATH_INFO'])

        # Check for error message in the response context
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertIn('There was a problem with the file upload', str(messages[0]))