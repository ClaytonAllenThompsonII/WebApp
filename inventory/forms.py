"""
Django forms for inventory data collection.

This module defines a form class, `inventoryDataCollectionForm`,
based on the Django `ModelForm`. It simplifies the creation and
processing of forms related to the InventoryItem model.

Imported Modules:
    - django.forms: Provides tools for working with forms.
    - .models.InventoryItem: The InventoryItem model.

Usage:
    - Import this module within a Django project's views to instantiate the form with request data.
    - Render the `InventoryDataCollectionForm` in templates to capture inventory data from users.

Requirements:
    - The InventoryItem model, as well as related GL level models, must be defined within the models.py file of the application.
"""

from django import forms
from .models import InventoryItem, GLLevel1, GLLevel2, GLLevel3, Product

class InventoryDataCollectionForm(forms.ModelForm):
    """A form class for collecting and validating data related to the
    InventoryItem model. It specifies the model and fields to include
    in the form.
    The form includes ModelChoiceField dropdowns for selecting General Ledger (GL) levels 
    and associated products, which are dynamically populated and constrained based on the 
    hierarchical relationships defined in the models.
 """
    gl_level_1 = forms.ModelChoiceField(queryset=GLLevel1.objects.all(), empty_label=None) # pylint: disable=no-member
    class Meta:
        """ Attributes:
        - gl_level_1 (ModelChoiceField): Dropdown field for selecting an instance of GLLevel1.
        - Meta.model (InventoryItem): The associated InventoryItem model.
        - Meta.fields (list): List of fields included in the form, corresponding to model attributes."""
        model = InventoryItem
        fields = ['image', 'gl_level_1', 'gl_level_2', 'gl_level_3', 'product']
