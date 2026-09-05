from django.shortcuts import render
from .models import Product

def home_page_view (request):
    return render(request, 'shop/index.html')

def product_list_view(request):
    products = Product.objects.filter(is_active=True)
    return render(request, 'shop/product_list.html', {'products': products})