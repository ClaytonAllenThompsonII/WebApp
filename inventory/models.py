"""Django models for inventory items. NEED TO REDO

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


  
# Model for GL Level 1
class GLLevel1(models.Model):
    """ Add Docstring """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f'{self.name}'

# Model for GL Level 2
class GLLevel2(models.Model):
    """ Add Docstring """
    parent = models.ForeignKey(GLLevel1, related_name='gl_level2', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f'{self.name}'

# Model for GL Level 3
class GLLevel3(models.Model):
    """ Add Docstring """
    parent = models.ForeignKey(GLLevel2, related_name='gl_level3', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f'{self.name}'

# Model for Product (could be directly linked to GL Level 3 or independent if needed)
class Product(models.Model):
    """ Add Docstring """
    parent = models.ForeignKey(GLLevel3, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f'{self.name}'



# Create your models here.
class InventoryItem(models.Model):
    """ NEED TO UPDATE DOC STRINGS
    Represents an inventory item with its associated image, label, timestamp, and user.
    
    Fields:
        - user (ForeignKey): The user who uploaded the inventory item. Indexed for faster query performance.
        - image (ImageField): The image file of the inventory item, stored in AWS S3.
        - type (CharField): The category or type of the inventory item. Indexed for faster query performance.
        - filename (CharField): The filename of the image in S3.
        - timestamp (DateTimeField): The time when the inventory item was added to the database.
        - gl_level_1
        - gl_level_2
        - gl_level_3
    """
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, db_index=True) # try User instead of get_user_model if needed.
    image = models.ImageField(upload_to='inventory_images/') #keep this to test, but get rid of after AWS works.
    filename = models.CharField(max_length=255) # to store the image filename in S3.
    timestamp = models.DateTimeField(auto_now_add=True)  # Add timestamp
    gl_level_1 = models.ForeignKey(GLLevel1, on_delete=models.CASCADE, null=True, blank=True)
    gl_level_2 = models.ForeignKey(GLLevel2, on_delete=models.CASCADE, null=True, blank=True)
    gl_level_3 = models.ForeignKey(GLLevel3, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        # Adjusted to handle cases where GL levels or product might be null
        product_name = self.product.name if self.product else 'No Product'
        return f'{self.user.username} - {product_name} ({self.timestamp})'
    