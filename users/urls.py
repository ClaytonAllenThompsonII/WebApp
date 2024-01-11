from django.urls import path
from . import views


urlpatterns = [
    path('', views.home),
    path('dashboard/', views.home),
    path('inventory/', views.inventory),
    path('invoices/', views.invoices),
    path('analytics/', views.analytics),
   
]