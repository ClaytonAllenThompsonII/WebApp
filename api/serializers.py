# api/serializers.py

from rest_framework import serializers
from invoice.models import ProductClassification  # adjust path if needed

class ProductClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductClassification
        fields = '__all__'