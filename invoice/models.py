"""
Module for defining the Invoice model.

This module contains the Invoice model class, which represents uploaded invoices
in the application. Each invoice is associated with a user and includes details
such as the uploaded PDF file, upload timestamp, and filename.

"""
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.functions import Lower
from django.core.exceptions import ValidationError


# Create your models here.

# Invoice Models 
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

    class Meta: 
        db_table = 'in_invoice_processing_upload'

    def __str__(self):
        return f"Invoice {self.filename} uploaded by {self.user.username} at {self.uploaded_at}"

class ProcessedVendor(models.Model):
    vendor_id = models.IntegerField(primary_key=True)  # IDs assigned during ELT
    most_recent_in_invoice_processing_id = models.IntegerField(null=True, blank=True)
    most_recent_s3_object_key = models.CharField(max_length=255, null=True, blank=True)
    most_recent_upload_date = models.DateTimeField(null=True, blank=True)
    account_number = models.CharField(max_length=255, null=True, blank=True)
    vendor_name = models.CharField(max_length=255, null=True, blank=True)
    vendor_short_name = models.CharField(max_length=255, null=True, blank=True)
    vendor_phone = models.CharField(max_length=15, null=True, blank=True)
    vendor_address = models.CharField(max_length=255, null=True, blank=True)
    vendor_street = models.CharField(max_length=255, null=True, blank=True)
    vendor_city = models.CharField(max_length=255, null=True, blank=True)
    vendor_state = models.CharField(max_length=2, null=True, blank=True)
    vendor_zip_code = models.CharField(max_length=10, null=True, blank=True)
    address_block = models.TextField(null=True, blank=True)
    vendor_remit_address = models.CharField(max_length=255, null=True, blank=True)
    remit_to_street = models.CharField(max_length=255, null=True, blank=True)
    remit_to_city = models.CharField(max_length=255, null=True, blank=True)
    remit_to_state = models.CharField(max_length=2, null=True, blank=True)
    remit_to_zip_code = models.CharField(max_length=10, null=True, blank=True)
    remit_to_address_block = models.TextField(null=True, blank=True)
    inserted_at = models.DateTimeField(auto_now_add=True)
    batched_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'out_vendor_processed'
        unique_together = ('vendor_short_name', 'account_number')
    
    def __str__(self):
        return self.vendor_name or 'Vendor'
    
class ProcessedInvoice(models.Model):
    invoice_id = models.IntegerField(primary_key=True) # IDs assigned during ELT
    # Use vendor_id directly as ForeignKey
    vendor = models.ForeignKey(
        'ProcessedVendor',  # The related model
        on_delete=models.SET_NULL,
        db_column='vendor_id',  # Use the same column name
        to_field='vendor_id',  # References vendor_id in the ProcessedVendor model
        null=True,
        blank=True,
        db_index=True  # Add index on this field
    )
    # Other fields
    in_invoice_processing_id = models.IntegerField()
    s3_object_key = models.CharField(max_length=255)
    upload_date = models.DateTimeField()
    account_number = models.CharField(max_length=255, null=True, blank=True)
    vendor_name = models.CharField(max_length=255)
    vendor_short_name = models.CharField(max_length=255, null=True, blank=True)  # Vendor's short name (new field)
    due_date = models.DateField(null=True, blank=True) # allow null values for now
    delivery_date = models.DateField(null=True, blank=True) # allow NULL values if needed
    invoice_receipt_date = models.DateField()
    invoice_number = models.CharField(max_length=255, unique=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    inserted_at = models.DateTimeField(auto_now_add=True)
    batched_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'out_invoice_processed'  # The actual table name in your PostgreSQL application db

class ProcessedLineItem(models.Model):
    line_item_id = models.IntegerField(primary_key=True)  # IDs assigned during ETL
    # Remove gl3_id and gl3_name fields
    # ForeignKey to GLLevel3
    gl3 = models.ForeignKey(
        'GLLevel3',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_index=True  # Optional: Add index to optimize lookups on gl3_id

    )
    # ForeignKey to ProcessedInvoice without db_column and to_field
    invoice = models.ForeignKey(
        'ProcessedInvoice',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        db_index=True  # Optional: Add index to optimize lookups on invoice_id

    )
    # ForeignKey to ProcessedProduct without db_column and to_field
    product = models.ForeignKey(
        'ProcessedProduct',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_index=True  # Optional: Add index to optimize lookups on product_id

    )
    # Other fields
    in_invoice_processing_id = models.IntegerField(null=True, blank=True)
    s3_object_key = models.TextField(null=True, blank=True)
    upload_date = models.DateTimeField(null=True, blank=True)
    invoice_receipt_id = models.TextField(null=True, blank=True)
    expense_document_index = models.IntegerField(null=True, blank=True)
    line_item_index = models.IntegerField(null=True, blank=True)
    product_code = models.TextField(null=True, blank=True)
    brand = models.TextField(null=True, blank=True)
    item_description = models.TextField(null=True, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    taxes = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit_of_measure = models.TextField(null=True, blank=True)
    pack = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    size = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    unit = models.TextField(null=True, blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    expense_row = models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'out_line_item_processed'
        indexes = [  # Optional: Additional indexes for performance
            models.Index(fields=['invoice'], name='idx_invoice'),
            models.Index(fields=['product'], name='idx_product'),
            models.Index(fields=['gl3'], name='idx_gl3'),
        ]

class ProcessedProduct(models.Model):
    # Primary key assigned during ELT, not auto-incremented
    product_id = models.IntegerField(primary_key=True)
    product_code = models.TextField(null=True, blank=True)
    item_description = models.TextField()
    brand = models.TextField(null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    # ForeignKey field to ProductClassification
    classification = models.ForeignKey(
        'ProductClassification',   # The related model
        on_delete=models.SET_NULL,
        db_column='classification_id',  # Column in this model's table storing the foreign key value
        to_field='classification_id',   # Field in the related model that this foreign key references
        null=True,
        blank=True
    )
    class Meta:
        db_table = 'out_product_processed'
        unique_together = ('product_code', 'item_description')

    def __str__(self):
        return self.item_description

class ProductClassification(models.Model):
    classification_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    enhanced_details = models.TextField(null=True, blank=True)
    storage_guidelines = models.TextField(null=True, blank=True)
    handling_instructions = models.TextField(null=True, blank=True)
    allergens = models.TextField(null=True, blank=True)
    nutritional_info = models.TextField(null=True, blank=True)
    regulatory_compliance = models.TextField(null=True, blank=True)
    shelf_life = models.IntegerField(null=True, blank=True)  # In days
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Validation logic to ensure unique classification name (case-insensitive)
        if ProductClassification.objects.filter(name__iexact=self.name).exclude(pk=self.pk).exists():
            raise ValidationError({'name': 'A classification with this name already exists.'})

    class Meta:
        db_table = 'dim_product_classification'
        constraints = [
            models.UniqueConstraint(
                Lower('name'),
                name='unique_productclassification_name_lower'
            )
        ]

    def __str__(self):
        return self.name


# Accounting Models ############################
# GLLevel1 Model
class GLLevel1(models.Model):
    gl1_id = models.AutoField(primary_key=True)
    gl1_name = models.CharField(max_length=100)
    gl1_code = models.CharField(max_length=20, unique=True, null=True, blank=True)  # Allow null temporarily

    class Meta:
        db_table = 'gl_level_1'

    def __str__(self):
        return self.gl1_name

# GLLevel2 Model
class GLLevel2(models.Model):
    gl2_id = models.AutoField(primary_key=True)
    gl1 = models.ForeignKey(GLLevel1, on_delete=models.CASCADE, related_name='gl_level_2')
    gl2_name = models.CharField(max_length=100)
    gl2_code = models.CharField(max_length=20, unique=True, null=True, blank=True)  # Allow null temporarily

    class Meta:
        db_table = 'gl_level_2'
        unique_together = ('gl1', 'gl2_code')

    def __str__(self):
        return self.gl2_name

# GLLevel3 Model
class GLLevel3(models.Model):
    gl3_id = models.AutoField(primary_key=True)
    gl2 = models.ForeignKey(GLLevel2, on_delete=models.CASCADE, related_name='gl_level_3')
    gl3_name = models.CharField(max_length=100)
    gl3_code = models.CharField(max_length=20, unique=True, null=True, blank=True)  # Allow null temporarily

    class Meta:
        db_table = 'gl_level_3'
        unique_together = ('gl2', 'gl3_code')

    def __str__(self):
        return self.gl3_name
# ConsolidatedGL Model
class ConsolidatedGL(models.Model):
    consolidated_gl_id = models.AutoField(primary_key=True)
    gl1_id = models.IntegerField(null=True, blank=True)
    gl1_name = models.CharField(max_length=100, null=True, blank=True)
    gl1_code = models.CharField(max_length=20, null=True, blank=True)
    gl2_id = models.IntegerField(null=True, blank=True)
    gl2_name = models.CharField(max_length=100, null=True, blank=True)
    gl2_code = models.CharField(max_length=20, null=True, blank=True)
    gl3_id = models.IntegerField(null=True, blank=True)
    gl3_name = models.CharField(max_length=100, null=True, blank=True)
    gl3_code = models.CharField(max_length=20, null=True, blank=True)

    class Meta:
        db_table = 'consolidated_gl'
        unique_together = ('gl3_id',)

    def __str__(self):
        return f"{self.gl1_name} > {self.gl2_name} > {self.gl3_name}"  
