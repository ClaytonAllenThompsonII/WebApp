"""
Module for defining forms related to image classification.

This module contains the form used to handle image uploads in the 
image classification application.
"""

from django import forms

class ImageUploadForm(forms.Form):
    """
    Form for uploading an image.

    This form contains a single field that allows users to upload an image file 
    which will be used for classification purposes.
    """
    
    image = forms.ImageField()  # Field for uploading the image file