from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.
# from django.contrib.auth.models import User use if I switch from get_user_model()

# Create your models here.
class InventoryItem(models.Model):
    """
    Represents an inventory item with its associated image, label, timestamp, and user.
    """
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE) # try User instead of get_user_model if needed. 
    image = models.ImageField(upload_to='inventory_images/')
    type = models.CharField(max_length=255) # had to change this from Label. Need to figure out what was up with that. I think I can give the HTML class an ID to rename it from type to label. 
    filename = models.CharField(max_length=255) # to store the image filename in S3.
    timestamp = models.DateTimeField(auto_now_add=True)  # Add timestamp

    def __str__(self):
        return f'{self.user.username} - {self.type} ({self.timestamp})'