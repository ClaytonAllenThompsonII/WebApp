# forms.py

from django import forms

class ImageUploadForm(forms.Form):
    """
    Form for uploading an image.

    This form contains a single field that allows users to upload an image file 
    which will be used for classification purposes.
    """
    image = forms.ImageField(label="Upload an Image", required=True)