from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('inventory/', views.InventoryView, name='inventory_app'),
]