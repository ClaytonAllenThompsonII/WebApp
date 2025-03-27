"""Update Module Doc String: """
from django.db import models
from django.contrib.auth import get_user_model
# from django.contrib.auth.models import User use if I switch from get_user_model()
from invoice.models import ProcessedProduct, GLLevel1, GLLevel2, GLLevel3

# Inventory Queue Item Model
class InventoryQueueItem(models.Model):
    inventory_item_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, db_index=True)
    filename = models.CharField(max_length=255) # S3 key
    timestamp = models.DateTimeField(auto_now_add=True) 
    product = models.ForeignKey(ProcessedProduct, null=True, blank=True, on_delete=models.SET_NULL)  # Reference ProcessedProduct
    size = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=50, null=True, blank=True)
    classification_result = models.JSONField(null=True, blank=True)
    inventory_cycle = models.ForeignKey('InventoryCollectionCycle', on_delete=models.CASCADE)

    def __str__(self):
        prod_desc = self.product.item_description if self.product else "No Product"
        return f'{self.user.username} - {prod_desc} ({self.timestamp})'

    class Meta:
        db_table = 'inventory_queue_items'


# Inventory Collection Cycle Model
class InventoryCollectionCycle(models.Model):
    cycle_id = models.BigAutoField(primary_key=True)  # Primary key for collection cycle
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)  # Link to user
    created_at = models.DateTimeField(auto_now_add=True)  # Auto-generated timestamp when the cycle is created
    committed = models.BooleanField(default=False)  # New field to mark when cycle is completed
    cycle_start = models.DateTimeField(null=True, blank=True)  # New fields for timing
    cycle_end = models.DateTimeField(null=True, blank=True)    # New fields for timing

    def __str__(self):
        return f'Cycle {self.cycle_id} - {self.user.username} ({self.created_at})'

    class Meta:
        db_table = 'inventory_collection_cycles'  # Custom database table name