from django import forms
from .models import InventoryItem

class inventoryDataCollectionForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['type', 'image']