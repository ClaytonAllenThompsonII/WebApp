from django.urls import path

from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('', views.home),
    path('dashboard/', views.home, name='dashboard'),
    path('invoices/', views.invoices, name='invoices'),
    path('analytics/', views.analytics, name='analytics'),
    path('register/', views.register, name='register'),
    path('login/', views.loginPage, name='loginPage'),
    path('logout/', views.logoutUser, name='logout'),
 
   
# https://stackoverflow.com/questions/67545932/how-can-i-send-a-reset-password-email-on-django
# Starting place reference. 
   path('reset_password/',
    auth_views.PasswordResetView.as_view(template_name="users/password_reset.html"),
    name="reset_password"),

   path('reset_password_sent/',
    auth_views.PasswordResetDoneView.as_view(template_name="users/password_reset_sent.html"),
    name="password_reset_done"), #FIX ME - only direct the user here if we successfully send an email. 

   path('reset/<uibd64>/<token>/',
    auth_views.PasswordResetConfirmView.as_view(), 
    name="password_reset_confirm"), # FIX ME - 

   path('reset_password_complete/', 
    auth_views.PasswordResetCompleteView.as_view(),
    name="password_reset_complete"),
]


"""
Handles the initial request to initiate a password reset.

- Displays the form for users to enter their email address.
- Sends a password reset email if a matching email is found.
- Redirects to the 'password_reset_done' view upon success.

1- Submit email form                        //PasswordResetView.as_view()
2- Email sent success message               //PasswordResetDoneView.as_view() 
3- Link to password Rest form in email      //PasswordResetConfirmView.as_view()
4- Password successfully changed message    //PasswordResetCompleteView.as_view()

"""

