"""
Module for defining forms related to invoice handling.

This module contains the InvoiceForm class, which is a ModelForm used for
uploading invoice PDF files.

"""
from django import forms
from .models import Invoice, ProcessedLineItem, ProcessedProduct, ProductClassification, GLLevel3
class InvoiceForm(forms.ModelForm):
    """ Form class for uploading invoice PDF files.

    This form class is a ModelForm for uploading invoice PDF files. It is
    associated with the Invoice model, allowing users to upload invoice files
    via a file input field """

    class Meta:
        """ Attributes:
        model (Invoice): The model associated with this form.
        fields (list): The fields to include in the form. """
        model = Invoice # Specifies the model associated with the form
        fields = ['pdf_file'] # Fields to include in the form



class ProcessedLineItemForm(forms.ModelForm):
    gl3_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    # Remove 'gl3' from the fields list

    class Meta:
        model = ProcessedLineItem
        fields = [
            'brand', 'item_description', 'unit_price',
            'net_amount', 'taxes', 'discount', 'quantity',
            'price', 'unit_of_measure', 'pack', 'size', 'unit',
            'weight'
            # Exclude 'gl3' from fields, we'll handle it in save()
        ]

    def save(self, commit=True):
        instance = super().save(commit=False)
        gl3_id = self.cleaned_data.get('gl3_id')
        if gl3_id:
            try:
                # Retrieve the GLLevel3 instance based on gl3_id
                gl3_instance = GLLevel3.objects.get(gl3_id=gl3_id)
                instance.gl3 = gl3_instance
            except GLLevel3.DoesNotExist:
                instance.gl3 = None
        else:
            instance.gl3 = None

        if commit:
            instance.save()
        return instance


class ProductForm(forms.ModelForm):
    class Meta:
        model = ProcessedProduct
        fields = [
            'item_description',  # Only allow editing of item description
            'brand',  # Allow editing of brand
        ]

class ProductClassificationForm(forms.ModelForm):
    class Meta:
        model = ProductClassification
        fields = [
            'name',
            'enhanced_details',
            'storage_guidelines',
            'handling_instructions',
            'allergens',
            'nutritional_info',
            'regulatory_compliance',
            'shelf_life'
        ]
        # Custom widgets to enhance the form display
        widgets = {
            'name': forms.TextInput(attrs={'id': 'id_name', 'class': 'form-control', 'placeholder': 'Classification name...'}),
            'enhanced_details': forms.Textarea(attrs={'id': 'id_enhanced_details', 'class': 'form-control', 'placeholder': 'Enhanced details...'}),
            'storage_guidelines': forms.Textarea(attrs={'id': 'id_storage_guidelines', 'class': 'form-control', 'placeholder': 'Storage guidelines...'}),
            'handling_instructions': forms.Textarea(attrs={'id': 'id_handling_instructions', 'class': 'form-control', 'placeholder': 'Handling instructions...'}),
            'allergens': forms.Textarea(attrs={'id': 'id_allergens', 'class': 'form-control', 'placeholder': 'Allergens...'}),
            'nutritional_info': forms.Textarea(attrs={'id': 'id_nutritional_info', 'class': 'form-control', 'placeholder': 'Nutritional info...'}),
            'regulatory_compliance': forms.Textarea(attrs={'id': 'id_regulatory_compliance', 'class': 'form-control', 'placeholder': 'Regulatory compliance...'}),
            'shelf_life': forms.NumberInput(attrs={'id': 'id_shelf_life', 'class': 'form-control', 'placeholder': 'Shelf life in days...'}),
        }

    # Validation logic
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if ProductClassification.objects.filter(name__iexact=name).exists():
            raise forms.ValidationError("A classification with this name already exists.")
        return name
