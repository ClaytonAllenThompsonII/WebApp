"""
Main URL configuration for the WebApp project.

This module defines the URL patterns for the entire project, 
including the admin interface, user management, and application-specific routes.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken import views


# add register, login, profile, logout paths. 
# If authenticated -> login, else register. 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('', include('inventory.urls')),
    path('invoice/', include('invoice.urls')),
    path('image-classifier/', include('image_classifier.urls')),  # Image classification tool
    path('api/', include('api.urls')),  # Our new API endpoints
    path('api-token-auth/', views.obtain_auth_token, name='api_token_auth'),
]
