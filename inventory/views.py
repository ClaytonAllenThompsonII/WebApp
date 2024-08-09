"""
Inventory Data Collection Views

This module provides Django views for handling inventory data collection,
image uploads, and product classification. Key features include:
- Rendering and processing inventory data collection forms.
- Dynamic cascading dropdowns for GL levels and product selection.
- Integration with AWS services for file storage and metadata management.

Key Views:
- `inventory_view`: Handles the display and processing of the inventory form.
- `get_gl_level_2`, `get_gl_level_3`, `get_products`: AJAX views for dynamic dropdown population.

Requirements:
- Django's authentication system for user access control.
- Dependencies on external models (GL levels, products) and storage backends (AWS S3, DynamoDB).
"""
import logging
from django.db import IntegrityError, DatabaseError
from django.utils import timezone
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from botocore.exceptions import BotoCoreError, ClientError
from django.http import JsonResponse


from invoice.models import ConsolidatedGL, Product, ProcessedLineItem

from .forms import InventoryDataCollectionForm
from .storage_backends import AWSStorageBackend


from .models import InventoryItem

logger = logging.getLogger(__name__)
# Create your views here.

#@login_required(login_url='loginPage')
#def inventory(request):
    #return render(request, 'inventory/inventory.html')


@login_required(login_url='loginPage')
def inventory_view(request):
    """ 
    Render and process the inventory data collection form.

    This view handles both GET and POST requests. On GET, it renders the form for
    inventory data submission. On POST, it processes the form data, including image
    uploads and classification, and saves the data to the database and AWS services.
     """
    print("Entered inventory_view function")  # Debug print
    if request.method == 'POST':
        print("POST request received")
        form = InventoryDataCollectionForm(request.POST, request.FILES) #Include request.FILES for image handling
        if form.is_valid():
            print("Form is valid. Processing the form")
            storage_backend = AWSStorageBackend() # instantiate storage backend.
            inventory_item = form.save(commit=False) # Create model instance without saving.
            inventory_item.user = request.user # set the user here

            # Set the name fields based on the selected objects
            if inventory_item.gl_level_1_id:
                gl1 = ConsolidatedGL.objects.get(gl1_id=inventory_item.gl_level_1_id.gl1_id)
                inventory_item.gl_level_1_name = gl1.gl1_name
            if inventory_item.gl_level_2_id:
                gl2 = ConsolidatedGL.objects.get(gl2_id=inventory_item.gl_level_2_id.gl2_id)
                inventory_item.gl_level_2_name = gl2.gl2_name
            if inventory_item.gl_level_3_id:
                gl3 = ConsolidatedGL.objects.get(gl3_id=inventory_item.gl_level_3_id.gl3_id)
                inventory_item.gl_level_3_name = gl3.gl3_name
            if inventory_item.product_id:
                product = Product.objects.get(product_id=inventory_item.product_id.product_id)
                inventory_item.product_name = product.name

            inventory_item.save()
            print(f"Selected GL Level 1 ID: {inventory_item.gl_level_1_id}")
            print(f"Selected GL Level 2 ID: {inventory_item.gl_level_2_id}")
            print(f"Selected GL Level 3 ID: {inventory_item.gl_level_3_id}")
            print(f"Selected Product ID: {inventory_item.product_id}")

            try:
                # Upload image to S3 and get filename
                filename = storage_backend.upload_file(form.cleaned_data['image'], user_id=request.user.id)
                inventory_item.filename = filename

                # Prepare and store metadata in DynamoDB
                item_data = {
                    'filename': {'S': filename},
                    'gl_level_1_id': {'S': str(inventory_item.gl_level_1_id.gl1_id)},
                    'gl_level_1_name': {'S': inventory_item.gl_level_1_name},
                    'gl_level_2_id': {'S': str(inventory_item.gl_level_2_id.gl2_id)},
                    'gl_level_2_name': {'S': inventory_item.gl_level_2_name},
                    'gl_level_3_id': {'S': str(inventory_item.gl_level_3_id.gl3_id)},
                    'gl_level_3_name': {'S': inventory_item.gl_level_3_name},
                    'product_id': {'S': str(inventory_item.product_id.product_id)},
                    'product_name': {'S': inventory_item.product_name},
                    'size': {'N': str(inventory_item.size) if inventory_item.size else '0'},
                    'unit': {'S': inventory_item.unit if inventory_item.unit else ''},
                    'timestamp': {'S': inventory_item.timestamp.strftime('%Y-%m-%d %H:%M:%S')},
                    'user_id': {'N': str(inventory_item.user.id)}  # Assuming user ID is a number
                }
                print("Attempting to create inventory item in DynamoDB")  # Debug print
                storage_backend.create_inventory_item(item_data)

                try:
                    inventory_item.save()  # Save model instance with S3 filename
                    print("Inventory item created and saved")  # Debug print
                except IntegrityError:
                    # This might happen if there's a duplicate entry, for instance
                    messages.error(request, "This item already exists.")
                    return redirect('inventory_app')  # Redirect to a safe page
                except DatabaseError:
                    # For other database-related issues
                    messages.error(request, "There was a problem saving the item. Please try again.")
                    return redirect('inventory_app')  # Redirect to a safe page    

                messages.success(request, f'Inventory item uploaded successfully on {timezone.localtime().strftime("%Y-%m-%d %H:%M:%S")}.')
                return redirect('inventory_app')  # Redirect back to the form
                #logger.info("file upload successful: %s", filename)
            
            except BotoCoreError as e:
                # Handle low-level exceptions from botocore
                logger.error(f"Botocore error during file upload to S3: {e}")
                messages.error(request, "There was a problem with the file upload. Please try again.")
                return redirect('inventory_app')  # Redirect back to the inventory form

            except ClientError as e:
                # Handle client errors from boto3's client methods
                logger.error(f"Client error during file upload to S3: {e}")
                messages.error(request, "There was a problem with the file upload service. Please try again.")
                return redirect('inventory_app')  # Redirect back to the inventory form

            except Exception as e:
                print(f"Error occurred: {e}")  # Debug print to log the exception
                messages.error(request, f'Error uploading inventory item: {e}')
                return redirect('inventory_app')  # Redirect back to the inventory form
        else:
            print("Form is invalid")
            print(form.errors)  # Print errors to debug
            messages.error(request, 'Invalid form submission. Please correct the errors.')  # Handle invalid form
    else:
        form = InventoryDataCollectionForm()

    two_days_ago = timezone.now() - timezone.timedelta(days=2)
    sort = request.GET.get('sort', '')  # Default to an empty string if not present

    # Determine the sorting
    if sort == 'timestamp_desc':
        order_by = '-timestamp'
    elif sort == 'timestamp_asc':
        order_by = 'timestamp'
    else:
        order_by = '-timestamp'  # Default sorting

    user_uploads = InventoryItem.objects.filter(
        user=request.user,
        timestamp__gte=two_days_ago,
        filename__isnull=False  # Assuming 'filename' being non-null means successfully uploaded to S3
        ).order_by('-timestamp')
        
 

    # Query all GL Level 1 instances to pass to the template
    gl_level1_objects = GLLevel1.objects.all()

    # Update the context to include GL Level 1 objects along with the form
    context = {'form': form,
               'user_uploads': user_uploads,
                'gl_level1_objects': gl_level1_objects,
                }
    return render(request, 'inventory/training_data.html', context)


@login_required(login_url='loginPage')
def get_gl_level_2(request):
    """
    Responds to AJAX requests with GL Level 2 options filtered by the selected GL Level 1 ID.
    
    Args:
        request: HttpRequest object containing GL Level 1 ID ('gl1_id') in GET parameters.
    
    Returns:
        JsonResponse containing a list of GL Level 2 items (id and name) related to the given GL Level 1.
    """
    gl1_id = request.GET.get('gl1_id')
    gl2_items = GLLevel2.objects.filter(parent_id=gl1_id) # pylint: disable=no-member
    gl2_data = [{'id': item.id, 'name': item.name} for item in gl2_items]
    return JsonResponse(gl2_data, safe=False)


@login_required(login_url='loginPage')
def get_gl_level_3(request):
    """
    Fetches and returns GL Level 3 options via AJAX, based on a selected GL Level 2 ID.
    
    Args:
        request: HttpRequest object with GL Level 2 ID ('gl2_id') provided in GET parameters.
    
    Returns:
        JsonResponse with a list of GL Level 3 items (id and name) associated with the specified GL Level 2.
    """
    gl2_id = request.GET.get('gl2_id')
    gl3_items = GLLevel3.objects.filter(parent_id=gl2_id) # pylint: disable=no-member
    gl3_data = [{'id': item.id, 'name': item.name} for item in gl3_items]
    return JsonResponse(gl3_data, safe=False)



@login_required(login_url='loginPage')
def get_products(request):
    """
    Provides AJAX functionality to retrieve products based on the selected GL Level 3 ID.
    
    Args:
        request: HttpRequest object that includes GL Level 3 ID ('gl3_id') in GET query parameters.
    
    Returns:
        JsonResponse with a list of products (id and name) under the chosen GL Level 3 category.
    """
    gl3_id = request.GET.get('gl3_id')
    products = Product.objects.filter(parent_id=gl3_id) # pylint: disable=no-member
    product_data = [{'id': product.id, 'name': product.name} for product in products]
    return JsonResponse(product_data, safe=False)

