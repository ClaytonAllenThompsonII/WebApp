"""Update Module Doc String: """


from django.db import models
from django.contrib.auth import get_user_model
# from django.contrib.auth.models import User use if I switch from get_user_model()
from invoice.models import ProcessedProduct, GLLevel1, GLLevel2, GLLevel3  # Ensure this import is correct



# Inventory Item Model
# Inventory Item Model
class InventoryItem(models.Model):
    inventory_item_id = models.BigAutoField(primary_key=True)  # Custom primary key
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, db_index=True)
    image = models.ImageField(upload_to='images/')
    filename = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    gl_level_1 = models.ForeignKey(GLLevel1, null=True, blank=True, on_delete=models.SET_NULL, related_name='inventory_items', db_column='gl_level_1_id')
    gl_level_1_name = models.CharField(max_length=100, null=True, blank=True)
    gl_level_2 = models.ForeignKey(GLLevel2, null=True, blank=True, on_delete=models.SET_NULL, related_name='inventory_items', db_column='gl_level_2_id')
    gl_level_2_name = models.CharField(max_length=100, null=True, blank=True)
    gl_level_3 = models.ForeignKey(GLLevel3, null=True, blank=True, on_delete=models.SET_NULL, related_name='inventory_items', db_column='gl_level_3_id')
    gl_level_3_name = models.CharField(max_length=100, null=True, blank=True)
    product = models.ForeignKey(ProcessedProduct, null=True, blank=True, on_delete=models.SET_NULL, db_column='product_id')  # Reference ProcessedProduct
    product_name = models.CharField(max_length=100, null=True, blank=True)
    size = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} - {self.product_name or "No Product"} ({self.timestamp})'

    class Meta:
        db_table = 'inventory_item_records'


# Inventory Queue Item Model
class InventoryQueueItem(models.Model):
    inventory_item_id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, db_index=True)
    image = models.ImageField(upload_to='images/')
    filename = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    gl_level_1 = models.ForeignKey(GLLevel1, null=True, blank=True, on_delete=models.SET_NULL, related_name='inventory_queue_items')
    gl_level_2 = models.ForeignKey(GLLevel2, null=True, blank=True, on_delete=models.SET_NULL, related_name='inventory_queue_items')
    gl_level_3 = models.ForeignKey(GLLevel3, null=True, blank=True, on_delete=models.SET_NULL, related_name='inventory_queue_items')
    product = models.ForeignKey(ProcessedProduct, null=True, blank=True, on_delete=models.SET_NULL)  # Reference ProcessedProduct
    product_name = models.CharField(max_length=100, null=True, blank=True)
    size = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit = models.CharField(max_length=50, null=True, blank=True)
    classification_result = models.JSONField(null=True, blank=True)
    inventory_cycle = models.ForeignKey('InventoryCollectionCycle', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} - {self.product_name or "No Product"} ({self.timestamp})'

    class Meta:
        db_table = 'inventory_queue_items'




# Inventory Collection Cycle Model
class InventoryCollectionCycle(models.Model):
    cycle_id = models.BigAutoField(primary_key=True)  # Primary key for collection cycle
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)  # Link to user
    created_at = models.DateTimeField(auto_now_add=True)  # Auto-generated timestamp when the cycle is created

    def __str__(self):
        return f'Cycle {self.cycle_id} - {self.user.username} ({self.created_at})'

    class Meta:
        db_table = 'inventory_collection_cycles'  # Custom database table name