from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import inventoryDataCollectionForm
from django.contrib import messages

# Create your views here.

#@login_required(login_url='loginPage')
#def inventory(request):
    #return render(request, 'inventory/inventory.html')


@login_required(login_url='loginPage')
def InventoryView(request):
    if request.method == 'POST':
        form = inventoryDataCollectionForm(request.POST, request.FILES)  # Include request.FILES for image handling
        if form.is_valid():
            form.save()  # Save form data to model
            messages.success(request, 'Yay success')
            # Handle successful submission (e.g., redirect, show success message)
    else:
        form = inventoryDataCollectionForm()
    # Render the template with the form
    context = {'form': form}
    return render(request, 'inventory/training_data.html', context)
