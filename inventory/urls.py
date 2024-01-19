"""Django URL patterns for the inventory app.

This module defines URL patterns for the inventory app in a Django
project. It includes a single URL pattern for the 'inventory/' endpoint,
mapped to the `inventory_view` function in the views module.

Imported Modules:
    - django.urls: Provides tools for defining URL patterns.
    - .views.inventory_view: The view function handling inventory data
      collection and submission.

Usage:
    1. Import this module in your Django project's urls.py file.
    2. Include the patterns defined in this module in the project's main
       urlpatterns.

URL Patterns:
    - 'inventory/': Maps to the `inventory_view` function, handling
      inventory data collection and submission. Named as 'inventory_app'."""

from django.urls import path
from . import views

urlpatterns = [
    path('inventory/', views.inventory_view, name='inventory_app'),
]
