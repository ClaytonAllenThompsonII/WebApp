from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.

def home(request):
    return render(request, 'users/dashboard.html')

def inventory(request):
    return render(request, 'users/inventory.html')

def invoices(request):
    return HttpResponse('invoices')

def analytics(request):
    return HttpResponse('analytics')


