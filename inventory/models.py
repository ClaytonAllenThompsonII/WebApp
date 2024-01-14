from django.db import models
from django.contrib.auth import get_user_model
# Create your models here.
from django.contrib.auth.models import User

# Create your models here.
class inventory_training(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE) # try User instead of get_user_model if needed. 
    image = models.ImageField(upload_to='inventory_images/')
    type = models.CharField(max_length=255)
    filename = models.CharField(max_length=255) # to store the image filename in S3.
    timestamp = models.DateTimeField(auto_now_add=True)  # Add timestamp

    def __str__(self):
        return f'{self.user.username} - {self.type} ({self.timestamp})'