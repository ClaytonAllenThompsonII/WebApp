from django.urls import path
from . import views


urlpatterns = [
    path('', views.home),
    path('dashboard/', views.home, name='dashboard'),
    path('inventory/', views.inventory, name='inventory'),
    path('invoices/', views.invoices, name='invoices'),
    path('analytics/', views.analytics, name='analytics'),
    path('register/', views.register, name='register'),
    path('login/', views.loginPage, name='loginPage'),
   
]