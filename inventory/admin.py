"""
Django admin configuration for managing InventoryItem models.

This module defines the admin configuration for the InventoryItem model 
in the Django admin interface. It includes the registration of the InventoryItem model with the 
admin site,allowing administrators to view and manage InventoryItem instances.

Imported Modules:
    - django.contrib.admin: The Django admin module providing tools for building admin interfaces.
    - .models.InventoryItem: The InventoryItem model from the current application's models module.

Usage:
    1. Import this module in your Django project's admin.py file.
    2. Ensure that the InventoryItem model is defined in the models.py file of the same application.
    3. Register the InventoryItem model with the admin site using the admin.site.register() function.
"""

from django.contrib import admin
from .models import InventoryItem
# Register your models here.


admin.site.register(InventoryItem)
