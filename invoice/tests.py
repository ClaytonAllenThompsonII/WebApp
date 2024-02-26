from django.test import TestCase, RequestFactory
from django.urls import reverse
import unittest
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from unittest.mock import Mock, patch, MagicMock
from invoice.s3_storage_backend import S3StorageBackend
from invoice.models import Invoice
from invoice.views import upload_invoice
from django.contrib.messages import get_messages
# Create your tests here.

class TestS3StorageBackend(unittest.TestCase):
    """Test case for the S3StorageBackend class.

This test case covers the functionality of the S3StorageBackend class,
including the invoice_file_upload method, by mocking the S3 client's upload_fileobj method
and verifying the correct arguments are passed when uploading a file to S3.
"""
    def setUp(self):
        # Create an instance of S3StorageBackend for testing
        self.storage_backend = S3StorageBackend()
        # Mock the S3 client
        self.storage_backend.s3_client = MagicMock()

        #self.storage_backend.multipart_threshold = 1024 * 1024 * 5  # Set the threshold to 5MB

#Passed
    def test_invoice_file_upload(self):
        """
    Test the invoice_file_upload method.

    This test mocks the S3 client's upload_fileobj method and
    verifies that the correct arguments are passed to the method
    when uploading a file to S3. It also checks if the method returns
    the expected filename.
    """
        # Mock the S3 client's upload_fileobj method
        mock_upload_fileobj = Mock()
        self.storage_backend.s3_client.upload_fileobj = mock_upload_fileobj

        # Mock the file object to be uploaded
        mock_file = Mock()
        mock_file.name = 'test_invoice.pdf'  # Mock the file name

        # Mock the user ID
        user_id = 123

        # Call the method to upload the file
        filename = self.storage_backend.invoice_file_upload(mock_file, user_id)

        # Assert that the S3 client's upload_fileobj method was called with the correct arguments
        expected_s3_key = f'invoices/user_{user_id}/test_invoice.pdf'
        mock_upload_fileobj.assert_called_once_with(mock_file, self.storage_backend.bucket_name, expected_s3_key)

        # Assert that the method returned the correct filename
        expected_filename = f'{user_id}_test_invoice.pdf'
        self.assertEqual(filename, expected_filename)


class TestUploadInvoiceView(TestCase):
    def setUp(self):
        # Create a test user
        self.user = get_user_model().objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')

        # Set up the request factory
        self.factory = RequestFactory()

    @patch('invoice.views.S3StorageBackend')
    def test_successful_invoice_upload(self, mock_s3_storage_backend):
        # Mock the invoice file
        mock_file = MagicMock(name='MockFile')
        mock_file.name = 'test_invoice.pdf'

        # Mock the form data
        form_data = {
            'pdf_file': mock_file,
            # Add other form fields if necessary
        }

        # Create a POST request with form data
        url = reverse('invoice:upload_invoice', current_app='invoice')
        request = self.factory.post(url, data=form_data)
        request.user = self.user

        # Mock the S3 storage backend to return a filename
        mock_storage_backend_instance = mock_s3_storage_backend.return_value
        mock_storage_backend_instance.invoice_file_upload.return_value = 'uploaded_invoice.pdf'

        # Call the view function
        response = upload_invoice(request)

        # Assert that the view redirects to the upload success page
        self.assertRedirects(response, reverse('invoice:upload_invoice'))

        # Assert that success message is displayed
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Invoice uploaded successfully to S3.')

if __name__ == '__main__':
    unittest.main()
