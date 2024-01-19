"""
Django forms for inventory data collection.

This module defines a form class, `inventoryDataCollectionForm`,
based on the Django `ModelForm`. It simplifies the creation and
processing of forms related to the InventoryItem model.

Imported Modules:
    - django.forms: Provides tools for working with forms.
    - .models.InventoryItem: The InventoryItem model.

Usage:
    1. Import this module in your Django project's forms.py file.
    2. Ensure the InventoryItem model is defined in models.py of
       the same application.
    3. Use the `inventoryDataCollectionForm` class in views or
       templates to handle inventory data collection forms.
Note:
    Ensure the InventoryItem model is properly defined in models.py
    and includes the specified fields in the form.
"""

from django import forms
from .models import InventoryItem

class inventoryDataCollectionForm(forms.ModelForm):
    """A form class for collecting and validating data related to the
    InventoryItem model. It specifies the model and fields to include
    in the form.
 """
    class Meta:
        """ Attributes:
            - model (InventoryItem): The associated InventoryItem model.
            - fields (list): Included fields from the InventoryItem model."""
        model = InventoryItem
        fields = ['type', 'image']
        