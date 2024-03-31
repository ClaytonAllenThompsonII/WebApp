"""
This module defines models related to user profiles and groups within the application.

The `Group` model represents a business or organization to which users can belong. 
Each group is identified by a unique name.

The `Profile` model extends the default Django `User` model with additional information, 
such as the user's associated group, phone number, and address. 
This model uses a one-to-one relationship with the `User` model to add user-specific information.

Both models leverage Django's built-in `id` fields for unique identification.
"""
from django.db import models
# Create your models here.
from django.contrib.auth.models import User, Group
    
class Profile(models.Model):
    """
    Extends the `User` model with additional profile information.

    Attributes:
        user (models.OneToOneField): A one-to-one link to Django's User model.
        group (models.ForeignKey): A link to the Group model, representing the group to which the user belongs.
        phone_number (models.CharField): The user's phone number.
        address (models.CharField): The user's address.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address_line_1 = models.CharField(max_length=255, blank=True, null=True)
    address_line_2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    zip_code = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        """Returns the user's username and group as its string representation."""
        # Check if the profile is associated with a group and adjust the string accordingly    
        return f'User {self.user.username} | Group: {self.group.name if self.group else "None"}'
    