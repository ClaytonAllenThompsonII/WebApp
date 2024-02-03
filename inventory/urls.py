"""Django URL patterns for the inventory app.

Defines URL patterns for managing inventory data collection in a Django project. This includes
the main view for inventory data submission and additional AJAX endpoints for dynamic dropdown
population based on user selections.

Imported Modules:
- django.urls: Tools for URL definitions.
- .views: Inventory app view functions for data handling.

Usage:
1. Import in the project's urls.py.
2. Use `include()` to add these patterns to the project's urlpatterns.

URL Patterns:
- 'inventory/': Main endpoint for inventory data submission.
- 'get_gl_level_2/': AJAX endpoint for GL Level 2 options.
- 'get_gl_level_3/': AJAX endpoint for GL Level 3 options.
- 'get_products/': AJAX endpoint for product options.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('inventory/', views.inventory_view, name='inventory_app'),
    path('get_gl_level_2/', views.get_gl_level_2, name='get_gl_level_2'),
    path('get_gl_level_3/', views.get_gl_level_3, name='get_gl_level_3'),
    path('get_products/', views.get_products, name='get_products'),
]
