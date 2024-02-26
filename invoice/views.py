""" Views for invoice app """
import logging
from django.db import IntegrityError, DatabaseError
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import InvoiceForm
from .s3_storage_backend import S3StorageBackend
from botocore.exceptions import BotoCoreError, ClientError

from .models import Invoice


logger = logging.getLogger(__name__)

# Create your views here.

@login_required(login_url='loginPage')
def upload_invoice(request):
    """ Handles invoice file upload and submission"""
    if request.method == 'POST':
        form = InvoiceForm(request.POST, request.FILES)
        if form.is_valid():
            print(" Form is valid. Processing the form")
            storage_backend = S3StorageBackend() # Instantiate the S3 storage backend
            invoice = form.save(commit=False) #Create model instance without saving.
            invoice.user = request.user # set the user here
            invoice.save()

            # invoice_file = form.cleaned_data['pdf_file']

            try:
                # Upload invoice file to S3 using the storage backend
                filename = storage_backend.invoice_file_upload(invoice.pdf_file, user_id=request.user.id)
                invoice.filename = filename
                invoice.save() # Save the model instance with the filename

                messages.success(request, 'Invoice uploaded successfully to S3.')
                return redirect('upload_invoice')
            

            except BotoCoreError as e:
                logger.error(f"Error uploading invoice to S3: {e}")
                messages.error(request, 'An error occurred while uploading the invoice. Please try again.')
                return redirect('upload_invoice')
            
            except ClientError as e:
                logger.error(f"Client error uploading invoice to S3: {e}")
                messages.error(request, 'A client error occurred while uploading the invoice. Please try again.')
                return redirect('upload_invoice')
            
            except Exception as e:
                logger.error(f"Unexpected error uploading invoice to S3: {e}")
                messages.error(request, 'An unexpected error occurred. Please try again later.')
                return redirect('upload_invoice')
        else:
            messages.error(request, 'Invalid form submission. Please correct the errors.')
            return redirect('upload_invoice')

    else:
        form = InvoiceForm()
    return render(request, 'invoice/upload_invoice.html', {'form': form})