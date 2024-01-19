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
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import InventoryDataCollectionForm


# Create your views here.

#@login_required(login_url='loginPage')
#def inventory(request):
    #return render(request, 'inventory/inventory.html')


@login_required(login_url='loginPage')
def inventory_view(request):
    """
    Handles inventory data collection and submission.

    - Renders the inventory data collection form.
    - Processes POST requests with form data.
    - Saves valid form data to the database.
    - Displays success messages upon successful submission.
    """
    if request.method == 'POST':
        form = InventoryDataCollectionForm(request.POST, request.FILES) #Include request.FILES for image handling
        if form.is_valid():
            form.save()  # Save form data to model
            messages.success(request, 'Yay success')
            # Handle successful submission (e.g., redirect, show success message)
    else:
        form = InventoryDataCollectionForm()
    # Render the template with the form
    context = {'form': form}
    return render(request, 'inventory/training_data.html', context)
