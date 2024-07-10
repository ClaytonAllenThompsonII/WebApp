""" Views for invoice app """
import logging
from django.db import IntegrityError, DatabaseError
from django.utils import timezone
from django.http import JsonResponse

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from botocore.exceptions import BotoCoreError, ClientError
from inventory.models import GLLevel1, GLLevel2, GLLevel3
from .s3_storage_backend import S3StorageBackend
from .models import Invoice, ProcessedInvoice, ProcessedLineItem, ConsolidatedGL


from .forms import ProcessedLineItemForm, InvoiceForm


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


            # Fetch user groups
            user_groups = request.user.groups.all()
            group = user_groups[0].name if user_groups else None  # Assuming the user belongs to only one group

            # invoice_file = form.cleaned_data['pdf_file']

            try:
                # Upload invoice file to S3 using the storage backend
                filename = storage_backend.invoice_file_upload(invoice.pdf_file, user_id=request.user.id, group=group)
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

    invoices = Invoice.objects.all().order_by('-uploaded_at')  # Order by upload date (optional)

    context = {'form': form,
               'invoices': invoices,
                }    
        
    return render(request, 'invoice/upload_invoice.html', context)


@login_required(login_url='loginPage')
def invoice_repo(request):
    """Displays a list of processed invoices in a table with sorting options."""
    sort_by = request.GET.get('sort_by', 'invoice_receipt_date')  # Default sorting by upload date
    order = request.GET.get('order', 'desc')  # Default to descending order

    if order == 'asc':
        invoices = ProcessedInvoice.objects.all().order_by(sort_by)
    else:
        invoices = ProcessedInvoice.objects.all().order_by('-' + sort_by)

    context = {
        'invoices': invoices,
        'sort_by': sort_by,
        'order': order,
    }
    return render(request, 'invoice/invoice_repo.html', context)


@login_required(login_url='loginPage')
def line_items_repo(request):
    sort_by = request.GET.get('sort_by', 'invoice_id')
    order = request.GET.get('order', 'asc')

    if order == 'desc':
        sort_by = f'-{sort_by}'

    line_items = ProcessedLineItem.objects.all().order_by(sort_by)
    context = {
        'line_items': line_items,
    }
    return render(request, 'invoice/invoice_line_item_list.html', context)



@login_required(login_url='loginPage')
def line_items_by_invoice(request, invoice_id):
    invoice = get_object_or_404(ProcessedInvoice, pk=invoice_id)
    line_items = ProcessedLineItem.objects.filter(invoice_id=invoice_id).order_by('expense_document_index', 'line_item_index')
    context = {
        'invoice': invoice,
        'line_items': line_items,
    }
    return render(request, 'invoice/line_items_by_invoice.html', context)


@login_required(login_url='loginPage')
def edit_line_item(request, line_item_id):
    line_item = get_object_or_404(ProcessedLineItem, line_item_id=line_item_id)
    
    # Initialize the S3 storage backend
    s3_backend = S3StorageBackend()
    # Generate the pre-signed URL
    s3_url = s3_backend.generate_presigned_url(line_item.s3_object_key)

     # Fetch GL Level 1, GL Level 2, and GL Level 3 data from ConsolidatedGL
    gl_level_1 = ConsolidatedGL.objects.values('gl_level_1_id', 'gl_level_1_name').distinct()
    gl_level_2 = ConsolidatedGL.objects.values('gl_level_2_id', 'gl_level_2_name').distinct()
    gl_level_3 = ConsolidatedGL.objects.values('gl_level_3_id', 'gl_level_3_name').distinct()

     # Print the pre-signed URL for debugging
    print("Generated S3 URL:", s3_url)
    
    if request.method == 'POST':
        form = ProcessedLineItemForm(request.POST, instance=line_item)
        if form.is_valid():
            form.save()
            return redirect('line_items_by_invoice', invoice_id=line_item.invoice_id)
    else:
        form = ProcessedLineItemForm(instance=line_item)
    
    context = {
        'line_item': line_item,
        'form': form,
        's3_url': s3_url,
        'gl_level_1': gl_level_1,  # Pass GL Level 1 data to the template
        'gl_level_2': gl_level_2,  # Pass GL Level 2 data to the template
        'gl_level_3': gl_level_3,  # Pass GL Level 3 data to the template
    }
    return render(request, 'invoice/edit_line_item.html', context)



@login_required(login_url='loginPage')
def general_ledger_accounts(request):
    gl_level_1 = GLLevel1.objects.all()
    gl_level_2 = GLLevel2.objects.all()
    gl_level_3 = GLLevel3.objects.all()
    
    context = {
        'gl_level_1': gl_level_1,
        'gl_level_2': gl_level_2,
        'gl_level_3': gl_level_3,
    }
    
    return render(request, 'invoice/general_ledger_accounts.html', context)