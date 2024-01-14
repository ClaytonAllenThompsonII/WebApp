from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CreateUserForm

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