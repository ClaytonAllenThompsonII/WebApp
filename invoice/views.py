""" Views for invoice app """
import logging
import json
import re
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import F
from django.db.models import OuterRef, Subquery

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction  # Import for atomic transactions
from django.contrib import messages
from botocore.exceptions import BotoCoreError, ClientError
from openai import OpenAI
from django.conf import settings

from inventory.models import InventoryQueueItem
from .s3_storage_backend import S3StorageBackend
from .models import Invoice, ProcessedInvoice, ProcessedLineItem, ConsolidatedGL, ProcessedProduct, ProductClassification
from .forms import ProcessedLineItemForm, InvoiceForm, ProductForm, ProductClassificationForm


# Set the OpenAI API key

logger = logging.getLogger(__name__)

# Create your views here.

#Invoice Views 
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

    two_days_ago = timezone.now() - timezone.timedelta(days=2)
    sort = request.GET.get('sort', '')  # Default to an empty string if not present

    # Determine the sorting
    if sort == 'timestamp_desc':
        order_by = '-timestamp'
    elif sort == 'timestamp_asc':
        order_by = 'timestamp'
    else:
        order_by = '-timestamp'  # Default sorting

    # IMPORTANT: Use the new InventoryQueueItem model
    user_uploads = InventoryQueueItem.objects.filter(
        user=request.user,
        timestamp__gte=two_days_ago,
        filename__isnull=False  # Files that have been successfully uploaded to S3
    ).order_by('-timestamp')

    invoices = Invoice.objects.all().order_by('-uploaded_at')  # Order by upload date (optional)

    context = {'form': form,
               'user_uploads': user_uploads,
               'invoices': invoices,
                }    
        
    return render(request, 'invoice/invoice_upload.html', context)


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


# Line Item Views
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

    # Base queryset for line items
    line_items = ProcessedLineItem.objects.filter(invoice_id=invoice_id).order_by('expense_document_index', 'line_item_index')

    # Subquery to fetch related ProductClassification fields
    classification_subquery = ProductClassification.objects.filter(classification_id=OuterRef('product__classification_id'))

    # Annotate the line_items queryset with all required fields
    line_items = line_items.annotate(
        product_classification_name=Subquery(classification_subquery.values('name')[:1]),
        classification_enhanced_details=Subquery(classification_subquery.values('enhanced_details')[:1]),
        classification_storage_guidelines=Subquery(classification_subquery.values('storage_guidelines')[:1]),
        classification_handling_instructions=Subquery(classification_subquery.values('handling_instructions')[:1]),
        classification_allergens=Subquery(classification_subquery.values('allergens')[:1]),
        classification_nutritional_info=Subquery(classification_subquery.values('nutritional_info')[:1]),
        classification_regulatory_compliance=Subquery(classification_subquery.values('regulatory_compliance')[:1]),
        classification_shelf_life=Subquery(classification_subquery.values('shelf_life')[:1]),
        # You can include 'created_at' if necessary, but it's often not needed in the tooltip
    )

    # Get all invoice IDs for navigation
    invoices = ProcessedInvoice.objects.order_by('invoice_id')  # Adjust ordering as needed
    invoice_ids = list(invoices.values_list('invoice_id', flat=True))

    current_index = invoice_ids.index(invoice_id)
    previous_invoice_id = invoice_ids[current_index - 1] if current_index > 0 else None
    next_invoice_id = invoice_ids[current_index + 1] if current_index < len(invoice_ids) - 1 else None

    # Count the number of unmapped items
    unmapped_count = line_items.filter(gl3__isnull=True).count()

    context = {
        'invoice': invoice,
        'line_items': line_items,
        'unmapped_count': unmapped_count,
        'previous_invoice_id': previous_invoice_id,
        'next_invoice_id': next_invoice_id,
    }
    return render(request, 'invoice/line_items_by_invoice.html', context)

@login_required(login_url='loginPage')
def edit_line_item(request, line_item_id):
    # Retrieve the specific line item or return a 404 error if not found
    line_item = get_object_or_404(ProcessedLineItem, line_item_id=line_item_id)

    # Initialize the S3 storage backend and generate a pre-signed URL for the PDF
    s3_backend = S3StorageBackend()
    s3_url = s3_backend.generate_presigned_url(line_item.s3_object_key)

    # Fetch consolidated GL data for dropdowns or selections in the form
    gl_level_1 = ConsolidatedGL.objects.values('gl1_id', 'gl1_name').distinct()
    gl_level_2 = ConsolidatedGL.objects.values('gl2_id', 'gl2_name').distinct()
    gl_level_3 = ConsolidatedGL.objects.all().values('gl1_name', 'gl2_name', 'gl3_name', 'gl3_id')

    # Attempt to fetch the associated Product; set to None if it doesn't exist
    try:
        product = ProcessedProduct.objects.get(product_id=line_item.product_id)
    except (ProcessedProduct.DoesNotExist, TypeError, ValueError):
        product = None

    if request.method == 'POST':
        # Bind the form with POST data and associate it with the existing line item instance
        form = ProcessedLineItemForm(request.POST, instance=line_item)
        
        if form.is_valid():
            with transaction.atomic():  # Start an atomic transaction to ensure all-or-nothing updates
                # Save the updated line item
                updated_line_item = form.save()
                updated_gl3 = updated_line_item.gl3  # Get the related GLLevel3 instance

                if updated_gl3:
                    updated_gl3_id = updated_gl3.gl3_id
                    updated_gl3_name = updated_gl3.gl3_name
                else:
                    updated_gl3_id = None
                    updated_gl3_name = None

                # Bulk update all other line items with the same Product_ID to have the same GL3 mapping
                ProcessedLineItem.objects.filter(
                    product_id=updated_line_item.product_id
                ).exclude(line_item_id=updated_line_item.line_item_id).update(
                    gl3=updated_gl3
                )

                # Optional: Log the update for auditing purposes
                # logger.info(f"GL3 mapping updated for Product ID {updated_line_item.product_id} by User {request.user.username}")

            # Provide success feedback to the user
            messages.success(request, "Line item and all associated products have been updated successfully.")
            return redirect('line_items_by_invoice', invoice_id=line_item.invoice_id)
        else:
            # Provide error feedback if the form is invalid
            messages.error(request, "Please correct the errors below.")
    else:
        # Initialize an unbound form with the existing line item instance for GET requests
        form = ProcessedLineItemForm(instance=line_item)

    # Fetch all line items for the current invoice, ordered by their index
    line_items = ProcessedLineItem.objects.filter(invoice_id=line_item.invoice_id).order_by('line_item_index')
    line_item_ids = list(line_items.values_list('line_item_id', flat=True))
    
    # Determine the current index of the line item to identify previous and next items
    try:
        current_index = line_item_ids.index(line_item.line_item_id)
    except ValueError:
        current_index = -1  # Handle cases where the line_item_id is not found

    # Identify the previous line item ID if it exists
    previous_line_item_id = line_item_ids[current_index - 1] if current_index > 0 else None
    # Identify the next line item ID if it exists
    next_line_item_id = line_item_ids[current_index + 1] if current_index < len(line_item_ids) - 1 else None

    context = {
        'line_item': line_item,
        'product': product,  # Pass the associated product to the template
        'form': form,  # Pass the form to the template
        's3_url': s3_url,  # Pass the S3 pre-signed URL for PDF viewing
        'gl_level_1': gl_level_1,  # Pass GL Level 1 data for dropdowns
        'gl_level_2': gl_level_2,  # Pass GL Level 2 data for dropdowns
        'gl_level_3': gl_level_3,  # Pass GL Level 3 data for dropdowns
        'previous_line_item_id': previous_line_item_id,  # Pass previous line item ID for navigation
        'next_line_item_id': next_line_item_id,  # Pass next line item ID for navigation
    }

    # Render the edit_line_item.html template with the provided context
    return render(request, 'invoice/edit_line_item.html', context)


# Product Views
@login_required(login_url='loginPage')
def product_enhancement(request):
    # Prefetch related models for efficiency
    vendor_subquery = ProcessedLineItem.objects.filter(
        product=OuterRef('pk'),
        invoice__vendor__vendor_short_name__isnull=False
    ).order_by('invoice__vendor__vendor_short_name').values('invoice__vendor__vendor_short_name')[:1]

    products = ProcessedProduct.objects.annotate(
        vendor_short_name=Subquery(vendor_subquery)
    ).prefetch_related(
        'processedlineitem_set__invoice__vendor',
        'processedlineitem_set__gl3'
    ).order_by('vendor_short_name', 'item_description')

    vendor_short_names_list = products.values_list('vendor_short_name', flat=True)
    vendor_short_names_set = set()
    for vendor in vendor_short_names_list:
        vendor_short_names_set.add(vendor.strip() if vendor and vendor.strip() else 'None')

    vendor_short_names = sorted(vendor_short_names_set)
    classifications = ProductClassification.objects.all()

    # Instantiate forms
    product_form = ProductForm(request.POST or None)
    classification_form = ProductClassificationForm(request.POST or None)

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        if not product_id:
            messages.error(request, "Product ID is missing!")
            return redirect('product_enhancement')

        product = get_object_or_404(ProcessedProduct, pk=product_id)
        product_form = ProductForm(request.POST, instance=product)

        # Process product form
        if product_form.is_valid():
            product_form.save()
        else:
            messages.error(request, "Please correct the product form errors.")
            return render(request, 'invoice/product_enhancement.html', {
                'products': products,
                'classifications': classifications,
                'product_form': product_form,
                'classification_form': classification_form,
            })

        # Handle classification update
        classification_id = request.POST.get('classification_id')

        if classification_id:  # If an existing classification is selected
            classification = get_object_or_404(ProductClassification, pk=classification_id)
            product.classification = classification
            product.save()
            print(f"Product classification updated with existing classification: {classification.name}")
        elif classification_form.is_valid():  # If creating a new classification
            classification = classification_form.save(commit=False)
            classification.save()
            product.classification = classification
            product.save()
            print(f"New classification created: {classification.name}")
        else:
            messages.error(request, "Please correct the classification form errors.")
            return render(request, 'invoice/product_enhancement.html', {
                'products': products,
                'classifications': classifications,
                'product_form': product_form,
                'classification_form': classification_form,
            })

        messages.success(request, "Product and classification updated successfully!")
        return redirect('product_enhancement')

    # Render for GET request
    context = {
        'products': products,
        'classifications': classifications,
        'product_form': product_form,
        'classification_form': classification_form,
        'vendor_short_names': vendor_short_names,
    }
    return render(request, 'invoice/product_enhancement.html', context)

@login_required(login_url='loginPage')
def get_classification_details(request, classification_id):
    try:
        classification = ProductClassification.objects.get(pk=classification_id)
        data = {
            'name': classification.name,
            'enhanced_details': classification.enhanced_details,
            'storage_guidelines': classification.storage_guidelines,
            'handling_instructions': classification.handling_instructions,
            'allergens': classification.allergens,
            'nutritional_info': classification.nutritional_info,
            'regulatory_compliance': classification.regulatory_compliance,
            'shelf_life': classification.shelf_life
        }
        return JsonResponse(data)
    except ProductClassification.DoesNotExist:
        return JsonResponse({'error': 'Product Classification not found'}, status=404)



@csrf_exempt
@login_required(login_url='loginPage')
def generate_product_name(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        
        if not product_id:
            return JsonResponse({'error': 'Product ID not provided'}, status=400)

        try:
            product = ProcessedProduct.objects.get(product_id=product_id)
        except ProcessedProduct.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)

        # Generate prompt
        prompt = (
            f"Generate a concise and accurate product name for the following details:\n"
            f"Item Description: {product.item_description}\n"
            f"Brand: {product.brand}\n"
        )

        try:
            # Call OpenAI API
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an assistant skilled in generating product names."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Log the response for debugging
            print(f"OpenAI API Response: {response}")

            generated_name = response.choices[0].message.content.strip()
            return JsonResponse({'generated_product_name': generated_name})

        except Exception as e:
            print(f"OpenAI API Error: {e}")  # Log the error
            return JsonResponse({'error': 'Error generating product name'}, status=500)


@csrf_exempt
@login_required(login_url='loginPage')
def enhance_product_details(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        
        if not product_id:
            return JsonResponse({'error': 'Product ID not provided'}, status=400)

        try:
            product = ProcessedProduct.objects.get(product_id=product_id)
            line_items = ProcessedLineItem.objects.filter(product_id=product_id)
        except ProcessedProduct.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)
        
        # Retrieve related data from ProcessedLineItems and other fields
        line_items_description = ", ".join([li.item_description for li in line_items if li.item_description])
        expense_rows = ", ".join([li.expense_row for li in line_items if li.expense_row])
        gl3_names = ", ".join([li.gl3.gl3_name for li in line_items if li.gl3 and li.gl3.gl3_name])

        # Build the prompt for OpenAI GPT-4 API
        prompt = (
            f"Using the following product information, generate detailed content for the fields: "
            f"'enhanced_details', 'storage_guidelines', 'handling_instructions', 'allergens', "
            f"'nutritional_info', 'regulatory_compliance', and 'shelf_life'.\n\n"
            f"Product Information:\n"
            f"- Item Description: {product.item_description}\n"
            f"- Brand: {product.brand or 'None'}\n"
            f"- Expense Rows: {expense_rows or 'None'}\n"
            f"- GL3 Name: {gl3_names or 'None'}\n"
            f"- Additional Line Item Descriptions: {line_items_description or 'None'}\n\n"
            f"Respond ONLY with a valid JSON object in the following format:\n"
            f"{{\n"
            f"  \"enhanced_details\": \"...\",\n"
            f"  \"storage_guidelines\": \"...\",\n"
            f"  \"handling_instructions\": \"...\",\n"
            f"  \"allergens\": \"...\",\n"
            f"  \"nutritional_info\": \"...\",\n"
            f"  \"regulatory_compliance\": \"...\",\n"
            f"  \"shelf_life\": number_of_days\n"
            f"}}\n"
            f"Do not include any explanations, apologies, or additional text. Ensure the JSON is valid and properly formatted."
        )

        try:
            # Call OpenAI API
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an assistant that generates detailed product classification data in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=500
            )

            # Extract and parse the generated JSON
            generated_text = response.choices[0].message.content.strip()

            # Extract JSON from the response
            
            json_match = re.search(r'\{.*\}', generated_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                try:
                    generated_data = json.loads(json_str)
                except json.JSONDecodeError as e:
                    print(f"JSON Decode Error: {e}\nOpenAI response: {generated_text}")
                    return JsonResponse({'error': 'Invalid JSON response from OpenAI API'}, status=500)
            else:
                print(f"Unable to extract JSON from OpenAI response: {generated_text}")
                return JsonResponse({'error': 'Invalid response format from OpenAI API'}, status=500)

            return JsonResponse(generated_data)

        except Exception as e:
            print(f"OpenAI API Error: {e}")
            return JsonResponse({'error': 'Error generating product details'}, status=500)
        
    return JsonResponse({'error': 'Invalid request'}, status=400)


# Add comments, Doc strings; 


# General Ledger Accounting

@login_required(login_url='loginPage')
def general_ledger_accounts(request):
    gl_level_1 = ConsolidatedGL.objects.values('gl1_id', 'gl1_name').distinct()
    gl_level_2 = ConsolidatedGL.objects.values('gl2_id', 'gl2_name', 'gl1_id').distinct()

    gl_level_3 = ConsolidatedGL.objects.all().values('gl1_name', 'gl2_name', 'gl3_name', 'gl3_id')
    
    context = {
        'gl_level_1': gl_level_1,
        'gl_level_2': gl_level_2,
        'gl_level_3': gl_level_3
    }
    
    return render(request, 'invoice/general_ledger_accounts.html', context)

@login_required(login_url='loginPage')
def get_gl_level_2(request):
    gl1_id = request.GET.get('gl1_id')
    if gl1_id:
        gl2_items = ConsolidatedGL.objects.filter(gl1_id=gl1_id).values('gl2_id', 'gl2_name').distinct()
        return JsonResponse(list(gl2_items), safe=False)
    return JsonResponse({"error": "GL Level 1 ID not provided"}, status=400)

@login_required(login_url='loginPage')
def gl_level_3_by_gl1(request):
    gl1_id = request.GET.get('gl1_id')
    if gl1_id:
        gl3_items = ConsolidatedGL.objects.filter(gl1_id=gl1_id).values('gl1_name', 'gl2_name', 'gl3_name', 'gl3_id')
    else:
        # Return all GL Level 3 items when gl1_id is not provided
        gl3_items = ConsolidatedGL.objects.all().values('gl1_name', 'gl2_name', 'gl3_name', 'gl3_id')
    return JsonResponse(list(gl3_items), safe=False)

@login_required(login_url='loginPage')
def gl_level_3_by_gl2(request):
    gl1_id = request.GET.get('gl1_id')
    gl2_id = request.GET.get('gl2_id')
    if gl1_id and gl2_id:
        gl3_items = ConsolidatedGL.objects.filter(gl1_id=gl1_id, gl2_id=gl2_id).values('gl1_name', 'gl2_name', 'gl3_name', 'gl3_id')
        print(f"Data for GL1 ID {gl1_id} and GL2 ID {gl2_id}: {list(gl3_items)}")  # Debugging line
        return JsonResponse(list(gl3_items), safe=False)
    return JsonResponse({"error": "GL Level 1 ID or GL Level 2 ID not provided"}, status=400)

