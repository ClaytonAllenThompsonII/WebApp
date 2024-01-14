from django import forms
from .models import inventory_training

class inventoryDataCollectionForm(forms.ModelForm):
    class Meta:
        model = inventory_training
        fields = ['type', 'image']