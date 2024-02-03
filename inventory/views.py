"""
Django Views for Inventory Data Collection.

This module provides a suite of views to support inventory data collection within a Django web
application. It facilitates the inventory management process from data input by users to backend
processing and storage.

Key Components:
- `inventory_view`: Renders the inventory data collection form. It handles GET and POST requests,
  processing form data for submissions and saving it to the database. User success notifications
  are managed through this view, secured with `@login_required` to ensure only authenticated users
  can submit data.

- AJAX Views (`get_gl_level_2`, `get_gl_level_3`, `get_products`): Enhance user experience by
  dynamically updating dropdown fields based on previous selections. They provide JSON data for
  cascading dropdown options, facilitating a hierarchical selection process.

Modules and Frameworks Utilized:
- `django.shortcuts`: Facilitates rendering templates and redirecting URLs.
- `django.contrib.auth.decorators`: Contains `@login_required` for access control.
- `django.contrib.messages`: Enables queuing and displaying messages to users.
- `forms.inventoryDataCollectionForm`: Custom form class specifying the structure and validation
  criteria for the data collection form.

Usage Guidelines:
1. Incorporate into your project's `views.py` to use the defined views for inventory management.
2. Map `inventory_view` to a URL pattern in `urls.py` for the form endpoint.
3. Map AJAX views similarly and utilize with JavaScript for dynamic form field population.

This module aims to streamline inventory item management, ensuring data integrity, enhancing user
experience, and maintaining secure access to functionalities.

    Decorators:
        - @login_required(login_url='loginPage'): Ensures that only
          authenticated users can access the view. Redirects to the
          login page if the user is not authenticated.
 """
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import InventoryDataCollectionForm
from .storage_backends import AWSStorageBackend

from django.http import JsonResponse
from .models import GLLevel1
from .models import GLLevel2
from .models import GLLevel3
from .models import Product

logger = logging.getLogger(__name__)
# Create your views here.

#@login_required(login_url='loginPage')
#def inventory(request):
    #return render(request, 'inventory/inventory.html')


@login_required(login_url='loginPage')
def inventory_view(request):
    """ Handles inventory data collection and submission. """
    print("Entered inventory_view function")  # Debug print
    if request.method == 'POST':
        print("POST request received")
        form = InventoryDataCollectionForm(request.POST, request.FILES) #Include request.FILES for image handling
        if form.is_valid():
            print("Form is valid")
            storage_backend = AWSStorageBackend() # instantiate storage backend.
            inventory_item = form.save(commit=False) # Create model instance without saving.
            inventory_item.user = request.user # set the user here
            inventory_item.save()

            try:
                # Upload image to S3 and get filename
                filename = storage_backend.upload_file(form.cleaned_data['image'], user_id=request.user.id)
                inventory_item.filename = filename

                # Prepare and store metadata in DynamoDB
                item_data = {
                    'filename': {'S': filename},
                    'gl_level_1_id': {'S': str(inventory_item.gl_level_1.id)},
                    'gl_level_1_name': {'S': inventory_item.gl_level_1.name},
                    'gl_level_2_id': {'S': str(inventory_item.gl_level_2.id)},
                    'gl_level_2_name': {'S': inventory_item.gl_level_2.name},
                    'gl_level_3_id': {'S': str(inventory_item.gl_level_3.id)},
                    'gl_level_3_name': {'S': inventory_item.gl_level_3.name},
                    'product_id': {'S': str(inventory_item.product.id)},
                    'product_name': {'S': inventory_item.product.name},
                    'timestamp': {'S': inventory_item.timestamp.strftime('%Y-%m-%d %H:%M:%S')},
                    'user_id': {'N': str(inventory_item.user.id)}  # Assuming user ID is a number
                }
                print("Attempting to create inventory item in DynamoDB")  # Debug print
                storage_backend.create_inventory_item(item_data)

                inventory_item.save()  # Save model instance with S3 filename
                print("Inventory item created and saved")  # Debug print

                messages.success(request, 'Inventory item uploaded successfully!')
                return redirect('inventory_view')  # Redirect back to the form
                #logger.info("file upload successful: %s", filename)
            except Exception as e:
                print(f"Error occurred: {e}")  # Debug print to log the exception
                messages.error(request, f'Error uploading inventory item: {e}')
                # Implement more specific error handling here
        else:
            print("Form is invalid")
            messages.error(request, 'Invalid form submission. Please correct the errors.')  # Handle invalid form
    else:
        form = InventoryDataCollectionForm()

    # Query all GL Level 1 instances to pass to the template
    gl_level1_objects = GLLevel1.objects.all()

    # Update the context to include GL Level 1 objects along with the form
    context = {'form': form, 'gl_level1_objects': gl_level1_objects}
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

