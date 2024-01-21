"""Django models for inventory items.

This module defines a Django model, `InventoryItem`, representing an
inventory item with its associated image, label, timestamp, and user.

Imported Modules:
    - django.db.models: Provides tools for defining database models.
    - django.contrib.auth: Provides tools for handling user authentication.
    - get_user_model: A function for dynamically retrieving the User model
      configured for the current Django project.

Usage:
    1. Import this module in your Django project's models.py file.
    2. Use the `InventoryItem` model to represent inventory items in the
       application's database.

Model `InventoryItem`:
    Represents an inventory item with the following fields:
    - user (ForeignKey): The user associated with the uploaded inventory item.
    - image (ImageField): The image file associated with the inventory item.
    - type (CharField): The type or label of the inventory item.
    - filename (CharField): The filename of the image file stored in S3.
    - timestamp (DateTimeField): Auto-generated timestamp indicating when
      the inventory item was added.

    Methods:
        - __str__(): Returns a string representation of the inventory item,
          including the username, type, and timestamp."""
from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.
# from django.contrib.auth.models import User use if I switch from get_user_model()

# Create your models here.
class InventoryItem(models.Model):
    """
    Represents an inventory item with its associated image, label, timestamp, and user.
    
    Fields:
        - user (ForeignKey): The user who uploaded the inventory item. Indexed for faster query performance.
        - image (ImageField): The image file of the inventory item, stored in AWS S3.
        - type (CharField): The category or type of the inventory item. Indexed for faster query performance.
        - filename (CharField): The filename of the image in S3.
        - timestamp (DateTimeField): The time when the inventory item was added to the database.
    """
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, db_index=True) # try User instead of get_user_model if needed.
    image = models.ImageField(upload_to='inventory_images/') #keep this to test, but get rid of after AWS works.
    type = models.CharField(max_length=255, db_index=True) # had to change this from Label. Need to figure out what was up with that. I think I can give the HTML class an ID to rename it from type to label.
    filename = models.CharField(max_length=255) # to store the image filename in S3.
    timestamp = models.DateTimeField(auto_now_add=True)  # Add timestamp

    def __str__(self):
        return f'{self.user.username} - {self.type} ({self.timestamp})'
    