from django.urls import path
from .views import image_classification_view

urlpatterns = [
    path('classify/', image_classification_view, name='image_classification_view'),
]