"""
Forms for inventory data collection.

This module defines the InventoryQueueItemForm based on Django's ModelForm
for handling inventory data related to the InventoryQueueItem model.

The form collects basic inventory details such as the product reference, size, 
and unit of measurement. The image file is not included in this form because it 
is uploaded separately to AWS S3 via our storage backend. Once the image is uploaded, 
its S3 key is stored in the model record (in the 'filename' field). In addition, 
classification results from the inference API (e.g., Hugging Face output) will be 
integrated into the record, simulating what our own model might eventually produce.

Usage:
    - Import and use this form in views to process inventory data input.
    - Render the form in templates to capture inventory details from users.

Requirements:
    - The InventoryQueueItem model must be defined in models.py.
"""

from django import forms
from .models import InventoryQueueItem

class InventoryQueueItemForm(forms.ModelForm):
    class Meta:
        model = InventoryQueueItem
        # Collect only the product, size, and unit fields. The image upload is handled separately.
        fields = ['product', 'size', 'unit']