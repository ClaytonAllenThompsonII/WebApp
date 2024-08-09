"""
Forms for inventory data collection.

This module defines the `InventoryDataCollectionForm` based on the `ModelForm` 
for handling inventory data related to the `InventoryItem` model.

Usage:
    - Import and use this form in views to handle inventory data input.
    - Render the form in templates to capture inventory data from users.

Requirements:
    - The `InventoryItem` model must be defined in models.py.
"""

from django import forms
from .models import InventoryItem


class InventoryDataCollectionForm(forms.ModelForm):
    """
    Form for collecting inventory data related to the InventoryItem model.
    """
    class Meta:
        model = InventoryItem
        fields = [
            'user', 'image', 'filename',
            'gl_level_1', 'gl_level_1_name',
            'gl_level_2', 'gl_level_2_name',
            'gl_level_3', 'gl_level_3_name',
            'product', 'product_name', 'size', 'unit'
        ]