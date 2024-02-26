""" URL configuration for the Invoice app.

This module defines the URL patterns for the Invoice app. It includes paths for
uploading invoices and other functionalities related to invoice management.

The `urlpatterns` list routes URLs to views defined in the `views.py` module of
the Invoice app. Each URL pattern is associated with a specific view function
that handles the corresponding HTTP request.

Namespace:
    The app namespace is set to 'invoice' to avoid naming conflicts with other
    apps in the project.

Example:
    To include these URL patterns in the project's main URL configuration,
    import this module and include it using the `include()` function:

    ```
    from django.urls import include, path

    urlpatterns = [
        path('invoice/', include('invoice.urls', namespace='invoice')),
    ]
    ``` """
from django.urls import path
from . import views

APP_NAME = 'invoice' # Invoice App namespace
urlpatterns = [
    path('upload/', views.upload_invoice, name='upload_invoice'),
    # Add other URL patterns as needed
]