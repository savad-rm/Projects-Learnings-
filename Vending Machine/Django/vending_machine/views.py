# vending_machine/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Product
from .forms import AdminLoginForm

def product_list(request):
    products = Product.objects.all()
    return render(request, 'vending_machine/product_list.html', {'products': products})

def view_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'vending_machine/view_product.html', {'product': product})

def admin_login(request):
    if request.method == 'POST':
        form = AdminLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('admin_dashboard')
    else:
        form = AdminLoginForm()
    return render(request, 'vending_machine/admin_login.html', {'form': form})

@login_required
def admin_dashboard(request):
    # Add admin dashboard logic here
    return render(request, 'vending_machine/admin_dashboard.html')

# @login_required
def admin_logout(request):
    logout(request)
    return redirect('product_list')

@login_required
def add_product(request):
    # Add logic for adding a product here
    return render(request, 'vending_machine/add_product.html')
