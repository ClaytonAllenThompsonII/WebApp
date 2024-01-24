"""Django views for handling inventory data collection.

This module defines views for inventory data collection in a Django
application. It includes a view function, `inventory_view`, which
handles the rendering of the inventory data collection form, processing
of form submissions, and saving valid form data to the database.

Imported Modules:
    - django.shortcuts: Provides shortcuts for common Django patterns.
    - django.contrib.auth.decorators: Provides decorators for handling
      authentication-related functionalities.
    - django.contrib.messages: Enables messages framework for displaying
      notifications to users.
    - .forms.inventoryDataCollectionForm: The form for collecting
      inventory data.

Usage:
    1. Import this module in your Django project's views.py file.
    2. Use the `inventory_view` function as a view for handling inventory
       data collection in the application.

Function `inventory_view`:
    Handles inventory data collection and submission.

    - Renders the inventory data collection form.
    - Processes POST requests with form data.
    - Saves valid form data to the database.
    - Displays success messages upon successful submission.

    Decorators:
        - @login_required(login_url='loginPage'): Ensures that only
          authenticated users can access the view. Redirects to the
          login page if the user is not authenticated.
 """
import logging
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import InventoryDataCollectionForm
from .storage_backends import AWSStorageBackend
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
                filename = storage_backend.upload_file(form.cleaned_data['image'])
                inventory_item.filename = filename

                # Prepare and store metadata in DynamoDB
                item_data = {
                    'filename': {'S': filename},
                    'label': {'S': inventory_item.type},
                    'timestamp': {'S': inventory_item.timestamp.strftime('%Y-%m-%d %H:%M:%S')},
                    'user_id': {'N': str(inventory_item.user.id)}  # Assuming user ID is a number
                }
                print("Attempting to create inventory item in DynamoDB")  # Debug print
                storage_backend.create_inventory_item(item_data)

                inventory_item.save()  # Save model instance with S3 filename
                print("Inventory item created and saved")  # Debug print

                messages.success(request, 'Inventory item uploaded successfully!')
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

    context = {'form': form}
    return render(request, 'inventory/training_data.html', context)
