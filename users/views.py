from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
# Create your views here.

def home(request):
    return render(request, 'users/dashboard.html')

def inventory(request):
    return render(request, 'users/inventory.html')

def invoices(request):
    return HttpResponse('invoices')

def analytics(request):
    return HttpResponse('analytics')


def register(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + user )
            return redirect('login')
        

    context = {'form': form}
    return render(request, 'users/register.html', context)


def loginPage(request):
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


def logoutUser(request):
    logout(request)
    return redirect('loginPage')