"""
Django AppConfig for the inventory app.

This module defines the Django AppConfig, `InventoryConfig`, for the
inventory app. It specifies the default auto field, app name, and a
unique label.

Imported Modules:
    - django.apps: Provides tools for configuring Django applications.

Usage:
    1. Include 'inventory.apps.InventoryConfig' in the 'INSTALLED_APPS'
       list of your Django project's settings.py file.
"""
from django.apps import AppConfig


class InventoryConfig(AppConfig):
    """ Django AppConfig for the inventory app. """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inventory' # app name
    label = 'inventory_app' # unique label
