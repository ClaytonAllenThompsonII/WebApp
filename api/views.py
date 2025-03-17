from django.shortcuts import render

# Create your views here.
# api/views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication

from invoice.models import ProductClassification
from .serializers import ProductClassificationSerializer

class ProductClassificationViewSet(viewsets.ModelViewSet):
    queryset = ProductClassification.objects.all()
    serializer_class = ProductClassificationSerializer
    

    # Removing auth; handled in settings.py
    # Option 1: If you didn't set the default auth in settings.py:
    #authentication_classes = [TokenAuthentication]
    #permission_classes = [IsAuthenticated]

    # Option 2: If you set the default TokenAuthentication in settings.py,
    # you only need: This is for testing
    #permission_classes = [AllowAny]