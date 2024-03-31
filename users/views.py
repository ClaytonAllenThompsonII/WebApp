from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm # ?
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CreateUserForm, UserProfileForm

from .models import Group, Profile




# Create your views here.

@login_required(login_url='loginPage')
def home(request):
    return render(request, 'users/dashboard.html')

@login_required(login_url='loginPage')
def invoices(request):
    return HttpResponse('invoices')

@login_required(login_url='loginPage')
def analytics(request):
    return HttpResponse('analytics')


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        user_form = CreateUserForm()
        profile_form = UserProfileForm()

        if request.method == 'POST':
            user_form = CreateUserForm(request.POST)
            profile_form = UserProfileForm(request.POST)
            if user_form.is_valid() and profile_form.is_valid():
                user = user_form.save()

                profile = profile_form.save(commit=False)
                profile.user = user
                # Since `group` is now a CharField, directly save the profile without group object creation
                profile.save()

                messages.success(request, f'Account was created for {user.username}!' )
                return redirect('loginPage')
    

        context = {'user_form': user_form, 'profile_form':profile_form}
        return render(request, 'users/register.html', context)


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    else:
        if request.method =='POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.info(request,'username OR password is incorrect')
            
        context = {}
        return render(request, 'users/login.html', context)

@login_required(login_url='loginPage')
def logoutUser(request):
    logout(request)
    return redirect('loginPage')