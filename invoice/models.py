"""
Module for defining the Invoice model.

This module contains the Invoice model class, which represents uploaded invoices
in the application. Each invoice is associated with a user and includes details
such as the uploaded PDF file, upload timestamp, and filename.

"""
from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.

class Invoice(models.Model):
    """ Model to store uploaded invoices.
        This model represents an invoice uploaded by a user """
    
     # FileField to store the PDF invoice file
    pdf_file = models.FileField(upload_to='invoices/')
    # DateTimeField to store the upload timestamp
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # ForeignKey to associate each invoice with a user who uploaded it
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, db_index=True)
    # CharField to store the filename of the uploaded invoice
    filename = models.CharField(max_length=255) # to store the image filename in S3.
    # Add other fields as needed

    def __str__(self):
        return f"Invoice {self.filename} uploaded by {self.user.username} at {self.uploaded_at}"
    