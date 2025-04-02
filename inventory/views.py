"""
Inventory Data Collection Views

This module provides Django views for handling inventory data collection, image uploads,
and product classification within the context of an inventory management system. The views support
inventory cycle management, dynamic product and classification selection, and integration with AWS 
for file storage and metadata management.

Key Features:
- Dynamic forms for inventory data collection, including product size, unit, and classification.
- Cascading dropdowns for GL Level 1, 2, and 3 categories, with AJAX-based population.
- Integration with AWS S3 for secure image uploads and metadata storage.
- Management of inventory cycles, including the ability to start, commit, and resume cycles.
- Tracking and storing inventory items related to active cycles and committed cycles.

Key Views:
- `inventory_queue_view`: Displays and manages the inventory queue, allowing users to see prioritized products, staged items, and selected product details.
- `save_inventory_data`: Saves new inventory data including size, unit, and uploaded images, and associates them with the active inventory cycle.
- `start_inventory_cycle`: Initializes a new inventory collection cycle for the user.
- `commit_inventory_cycle`: Marks the inventory cycle as complete and committed, finalizing data entry for the cycle.
- `manage_inventory_cycles`: Displays all inventory cycles associated with the user, including the ability to resume or delete uncommitted cycles.
- `get_gl_level_2`, `get_gl_level_3`, `get_products`: AJAX views for dynamically populating dropdowns based on GL level selections.
- `load_line_items`: Retrieves and displays detailed line items related to a selected product.
- `product_impact_index`: Calculates and displays the financial impact of products in terms of total spend, with support for visualization.

Requirements:
- Django authentication system for user access control.
- Integration with external models (ConsolidatedGL, ProcessedProduct, ProcessedLineItem) for GL categorization and product information.
- AWS S3 for image storage and DynamoDB for metadata handling.
- Dependencies on models for managing inventory cycles and items (InventoryCollectionCycle, InventoryQueueItem).
"""
import logging
import json

from django.db.models import Sum, Subquery, OuterRef, F, FloatField, Value, CharField
from django.db.models.functions import Coalesce, Cast, Concat
from django.views.decorators.http import require_POST
from django.conf import settings

from django.db.models.functions import Cast
from django.db import IntegrityError, DatabaseError
from django.http import JsonResponse
from django.utils import timezone
from django.utils.safestring import mark_safe

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from botocore.exceptions import BotoCoreError, ClientError
from django.utils.safestring import mark_safe

from invoice.models import ConsolidatedGL, ProcessedProduct, ProcessedLineItem, ProcessedInvoice, GLLevel1, GLLevel2, GLLevel3
from .models import InventoryQueueItem, InventoryCollectionCycle

from .forms import InventoryQueueItemForm
from .storage_backends import AWSStorageBackend


logger = logging.getLogger(__name__)
# Create your views here.

#@login_required(login_url='loginPage')
#def inventory(request):
    #return render(request, 'inventory/inventory.html')



@login_required(login_url='loginPage')
def get_gl_level_2(request):
    """
    Fetch and return GL Level 2 options based on the selected GL Level 1.

    This view is accessed via AJAX and returns a JSON response containing
    the GL Level 2 categories associated with the selected GL Level 1.
    """
    gl1_id = request.GET.get('gl1_id')
    print(f"Received GL Level 1 ID: {gl1_id}")  # Debugging line
    gl2_items = ConsolidatedGL.objects.filter(gl1_id=gl1_id).values('gl2_id', 'gl2_name').distinct()
    print(f"GL Level 2 items: {list(gl2_items)}")  # Debugging line
    gl2_data = [{'id': item['gl2_id'], 'name': item['gl2_name']} for item in gl2_items]
    return JsonResponse(gl2_data, safe=False)

@login_required(login_url='loginPage')
def get_gl_level_3(request):
    """
    Fetch and return GL Level 3 options based on the selected GL Level 2.

    This view is accessed via AJAX and returns a JSON response containing
    the GL Level 3 categories associated with the selected GL Level 2.
    """
    gl2_id = request.GET.get('gl2_id')
    gl3_items = ConsolidatedGL.objects.filter(gl2_id=gl2_id).values('gl3_id', 'gl3_name').distinct()
    gl3_data = [{'id': item['gl3_id'], 'name': item['gl3_name']} for item in gl3_items]
    return JsonResponse(gl3_data, safe=False)

@login_required(login_url='loginPage')
def get_products(request):
    """
    Fetch and return product options based on the selected GL Level 3.

    This view is accessed via AJAX and returns a JSON response containing
    the products associated with the selected GL Level 3.
    """
    # Get the gl3_id from the request
    gl3_id = request.GET.get('gl3_id')
    
    if gl3_id:
        # Filter ProcessedLineItem records with the given gl3_id
        line_items = ProcessedLineItem.objects.filter(gl3_id=gl3_id)
        
        # Collect unique product IDs from the filtered line items
        product_ids = line_items.values_list('product_id', flat=True).distinct()
        
        # Filter the Product records with the collected product IDs
        products = ProcessedProduct.objects.filter(product_id__in=product_ids)
        
        # Construct the list of dictionaries containing product details
        product_data = []
        for product in products:
            line_item = line_items.filter(product_id=product.product_id).first()
            product_data.append({
                'id': product.product_id,
                'name': product.generated_product_name or product.item_description,
                'gl3_name': line_item.gl3_name,
                'gl3_id': line_item.gl3_id
            })
        
        # Return the JSON response with the product data
        return JsonResponse(product_data, safe=False)
    else:
        # Return an error message if gl3_id is not provided
        return JsonResponse({'error': 'GL3 ID not provided'}, status=400)
################################################## Ver.1 ^ 


@login_required(login_url='loginPage')
def inventory_queue_view(request):
    # Subquery to calculate total spend per product
    total_spend_subquery = (
        ProcessedLineItem.objects
        .filter(product_id=OuterRef('product_id'))
        .values('product_id')
        .annotate(total=Sum('price'))
        .values('total')
    )

    # Fetch products with total spend and related classification
    products_with_spend = (
        ProcessedProduct.objects
        .annotate(total_spend=Subquery(total_spend_subquery))
        .select_related('classification')
        .order_by('classification_id', '-total_spend')  # First order by classification_id for DISTINCT ON
    )

    # Fetch distinct classifications with a representative product
    prioritized_products = (
        products_with_spend
        .filter(classification__isnull=False)
        .distinct('classification_id')  # Use classification_id for distinct
    )

    # Fetch selected product and line items if product_id is provided
    selected_product = None
    line_items = []
    product_id = request.GET.get('product_id')
    if product_id:
        selected_product = get_object_or_404(ProcessedProduct, pk=product_id)
        line_items = ProcessedLineItem.objects.filter(product_id=product_id)

    # Get the current user's details
    user = request.user
    profile = user.profile if hasattr(user, 'profile') else None

    # Get the active inventory cycle
    try:
        active_cycle = (
            InventoryCollectionCycle.objects
            .filter(user=user, committed=False)
            .latest('created_at')
        )
    except InventoryCollectionCycle.DoesNotExist:
        active_cycle = None

    # Fetch staged products with related product and classification
    staged_products = []
    if active_cycle:
        staged_products = InventoryQueueItem.objects.filter(inventory_cycle=active_cycle).select_related('product__classification')

    active_cycle_start = None
    if active_cycle and not active_cycle.committed:
        active_cycle_start = active_cycle.cycle_start

    context = {
        'prioritized_products': prioritized_products,  # Distinct classifications for unstaged products
        'selected_product': selected_product,
        'line_items': line_items,
        'staged_products': staged_products,
        'user_name': user.username,
        'user_id': user.id,
        'user_group': profile.group.name if profile and profile.group else 'None',
        'active_cycle': active_cycle,
        'active_cycle_start': active_cycle_start,
    }

    return render(request, 'inventory/inventory_queue.html', context)

@login_required(login_url='loginPage')
@require_POST
def save_inventory_data(request):
    product_id = request.POST.get('product_id')
    size = request.POST.get('size')
    unit = request.POST.get('unit')
    image = request.FILES.get('image')
    user = request.user

    # Retrieve the active inventory cycle
    try:
        active_cycle = InventoryCollectionCycle.objects.filter(user=user).latest('created_at')
    except InventoryCollectionCycle.DoesNotExist:
        return JsonResponse({'error': 'No active inventory cycle found.'}, status=400)

    # Instantiate the S3 storage backend
    storage_backend = AWSStorageBackend()
    
    # Retrieve group_id from user's profile
    group_id = user.profile.group.id if hasattr(user, 'profile') and user.profile.group else None
    if not group_id:
        return JsonResponse({'error': 'User group information not available.'}, status=400)
    
    # Upload image to S3 and get S3 key (passing product_id as well)
    try:
        s3_key = storage_backend.upload_file(
            image, 
            user_id=user.id, 
            group_id=group_id, 
            cycle_id=active_cycle.cycle_id, 
            product_id=product_id
        )
    except (BotoCoreError, ClientError, Exception) as e:
        return JsonResponse({'error': str(e)}, status=500)
    
    # Retrieve classification results from the hidden input
    classification_result_str = request.POST.get('classification_result')
    try:
        classification_result = json.loads(classification_result_str) if classification_result_str else None
    except json.JSONDecodeError:
        classification_result = None

    # Create a new InventoryQueueItem, storing the S3 key in the filename field
    inventory_item = InventoryQueueItem.objects.create(
        user=user,
        product_id=product_id,
        size=size,
        unit=unit,
        filename=s3_key,  # S3 key is stored here
        classification_result=classification_result,
        inventory_cycle=active_cycle
    )

    return JsonResponse({'message': 'Data successfully saved.'})


@login_required(login_url='loginPage')
@require_POST
def start_inventory_cycle(request):  # Added timing mechanism for gamification.
    if request.method == 'POST':
        new_cycle = InventoryCollectionCycle.objects.create(
            user=request.user,
            cycle_start=timezone.now()  # Set the start time
        )
        return JsonResponse({'success': True, 'cycle_id': new_cycle.cycle_id})
    return JsonResponse({'success': False}, status=400) 


@login_required(login_url='loginPage')
@require_POST
def commit_inventory_cycle(request): # need to have end time, to gamify. 
    user = request.user
    active_cycle = InventoryCollectionCycle.objects.filter(user=user).latest('created_at')
    
    # Mark the cycle as committed
    active_cycle.committed = True
    active_cycle.cycle_end = timezone.now()
    active_cycle.save()

    # Optionally, perform other actions here (e.g., generate reports, trigger notifications)

    return JsonResponse({'success': True, 'message': 'Inventory cycle committed.'})




@login_required(login_url='loginPage')
def load_line_items(request):
    product_id = request.GET.get('product_id')
    
    # Fetch line items for the selected product
    line_items = ProcessedLineItem.objects.filter(product_id=product_id)
    
    # Prepare the data to include invoice_receipt_date and other fields
    line_item_data = []
    for item in line_items:
        # Fetch the corresponding invoice to get the receipt date
        invoice = ProcessedInvoice.objects.filter(invoice_id=item.invoice_id).first()
        invoice_receipt_date = invoice.invoice_receipt_date if invoice else "N/A"

        line_item_data.append({
            'line_item_id': item.line_item_id,
            'item_description': item.item_description,
            'quantity': item.quantity,
            'unit': item.unit_of_measure,
            'price': item.price,
            'unit_price': item.unit_price,  # Added unit price
            'pack': item.pack,  # Added pack
            'size': item.size,  # Added size
            'weight': item.weight,  # Added weight
            'invoice_receipt_date': invoice_receipt_date,  # Add the invoice receipt date here
        })

    return JsonResponse({'line_items': line_item_data})
    

@login_required(login_url='loginPage')
def product_impact_index(request):

    # Step 1: Aggregate total spend per product using ProcessedLineItem.
    product_spend_subquery = (
        ProcessedLineItem.objects
        .filter(product_id=OuterRef('product_id'))
        .values('product_id')
        .annotate(total_spend=Sum('price'))
        .values('total_spend')
    )

    # Step 2: Annotate each ProcessedProduct with its total spend and an associated gl3_id.
    products = ProcessedProduct.objects.annotate(
        total_spend=Subquery(product_spend_subquery),
        gl3_id=Subquery(
            ProcessedLineItem.objects
            .filter(product_id=OuterRef('product_id'))
            .values('gl3_id')[:1]  # Get the first associated gl3_id
        )
    ).filter(total_spend__isnull=False)

    # Step 3: Annotate GL details from ConsolidatedGL and convert total_spend to float.
    products = products.annotate(
        gl1_name=Subquery(
            ConsolidatedGL.objects.filter(gl3_id=OuterRef('gl3_id')).values('gl1_name')[:1]
        ),
        gl2_name=Subquery(
            ConsolidatedGL.objects.filter(gl3_id=OuterRef('gl3_id')).values('gl2_name')[:1]
        ),
        gl3_name=Subquery(
            ConsolidatedGL.objects.filter(gl3_id=OuterRef('gl3_id')).values('gl3_name')[:1]
        ),
        total_spend_float=Cast('total_spend', output_field=FloatField())
    )

    # Step 4: Annotate a computed display name (brand + item_description).
    products = products.annotate(
        display_name=Concat('brand', Value(' '), 'item_description', output_field=CharField())
    )

    # Step 5: Order products by total spend in descending order.
    products = products.order_by('-total_spend')

    # Step 6: Prepare data for the heatmap visualization.
    product_spend_data = products.values(
        'product_id',
        'display_name',       # Computed name field
        'item_description',
        'total_spend_float'   # Float version of total spend
    )

    product_spend_data_json = mark_safe(json.dumps(list(product_spend_data)))

    # Step 7: Render the template with the context.
    context = {
        'product_spend': products,
        'product_spend_data': product_spend_data_json
    }
    return render(request, 'inventory/product_impact_index.html', context)
    # Step 1: Aggregate total spend per product_id from ProcessedLineItem
    product_spend_subquery = (
        ProcessedLineItem.objects
        .filter(product_id=OuterRef('product_id'))
        .values('product_id')
        .annotate(total_spend=Sum('price'))
        .values('total_spend')
    )

    # Step 2: Create a base queryset for Product, joining with ConsolidatedGL
    products = ProcessedProduct.objects.annotate(
        total_spend=Subquery(product_spend_subquery),
        gl3_id=Subquery(
            ProcessedLineItem.objects
            .filter(product_id=OuterRef('product_id'))
            .values('gl3_id')[:1]  # Get the first gl3_id associated with this product
        )
    ).filter(total_spend__isnull=False)

    # Step 3: Join with ConsolidatedGL to get GL details
    products = products.annotate(
        gl1_name=Subquery(
            ConsolidatedGL.objects.filter(gl3_id=OuterRef('gl3_id')).values('gl1_name')[:1]
        ),
        gl2_name=Subquery(
            ConsolidatedGL.objects.filter(gl3_id=OuterRef('gl3_id')).values('gl2_name')[:1]
        ),
        gl3_name=Subquery(
            ConsolidatedGL.objects.filter(gl3_id=OuterRef('gl3_id')).values('gl3_name')[:1]
        ),
        total_spend_float=Cast('total_spend', output_field=FloatField())  # Convert Decimal to Float
    )

    # Step 4: Order by total_spend in descending order
    products = products.order_by('-total_spend')

    # Prepare data for the heatmap visualization
    product_spend_data = products.values(
        'product_id',
        'generated_product_name',
        'item_description',
        'total_spend_float'  # Use the float version of total_spend
    )

    # Convert to JSON and mark safe
    product_spend_data_json = mark_safe(json.dumps(list(product_spend_data)))

    # Step 5: Prepare context and render the template
    context = {
        'product_spend': products,
        'product_spend_data': product_spend_data_json
    }
    return render(request, 'inventory/product_impact_index.html', context)



@login_required(login_url='loginPage')
def manage_inventory_cycles(request):
    """
    Displays all inventory cycles for the current user.
    Uncommitted cycles are shown with actions to resume or delete them.
    Committed cycles are listed as read-only.
    """
    cycles = InventoryCollectionCycle.objects.filter(user=request.user).order_by('-created_at')
    context = {
        'cycles': cycles,
    }
    return render(request, 'inventory/manage_inventory_cycles.html', context)

@login_required(login_url='loginPage')
@require_POST
def resume_inventory_cycle(request, cycle_id):
    """
    Resumes the selected uncommitted cycle.
    In a single-active approach, this could be stored in the session or a user profile field.
    For simplicity, we'll store it in the session.
    """
    cycle = get_object_or_404(InventoryCollectionCycle, cycle_id=cycle_id, user=request.user, committed=False)
    request.session['active_cycle_id'] = cycle_id  # Save active cycle id in session
    return JsonResponse({'success': True, 'message': f'Cycle {cycle_id} resumed.'})

@login_required(login_url='loginPage')
@require_POST
def delete_inventory_cycle(request, cycle_id):
    """
    Deletes an uncommitted cycle. Only uncommitted cycles can be deleted.
    """
    print("delete_inventory_cycle got called!")  # Quick debug

    cycle = get_object_or_404(InventoryCollectionCycle, cycle_id=cycle_id, user=request.user, committed=False)
    cycle.delete()
    return JsonResponse({'success': True, 'message': f'Cycle {cycle_id} deleted.'})