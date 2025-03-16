# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductClassificationViewSet

router = DefaultRouter()
router.register(r'productclassifications', ProductClassificationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]