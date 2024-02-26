"""
Module for defining forms related to invoice handling.

This module contains the InvoiceForm class, which is a ModelForm used for
uploading invoice PDF files.

"""
from django import forms
from .models import Invoice

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
