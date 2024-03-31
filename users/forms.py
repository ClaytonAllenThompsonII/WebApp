#from django.forms import ModelForm --- used for different method -- switched to UserCreationForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group

from .models import Profile
class CreateUserForm(UserCreationForm):
    """
   
    """
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2' ]

class UserProfileForm(forms.ModelForm):
    """
    A form for creating and updating user profiles.
    
    This form is linked to the Profile model and includes fields to capture
    additional information about the user, such as their phone number, address,
    and the group they belong to.
    """
    group = forms.ModelChoiceField(queryset=Group.objects.all(), required=True, help_text='Select your group.')
    phone_number = forms.CharField(max_length=15, required=True, help_text='Phone number.')
    address_line_1 = forms.CharField(max_length=255, required=True)
    # empty fields for additional address details
    address_line_2 = forms.CharField(max_length=255, required=False)
    city = forms.CharField(max_length=255, required=True)
    state = forms.CharField(max_length=255, required=True)
    zip_code = forms.CharField(max_length=255, required=True)

    class Meta:
        model = Profile
        fields = ['group', 'phone_number', 'address_line_1', 'address_line_2', 'city', 'state', 'zip_code']