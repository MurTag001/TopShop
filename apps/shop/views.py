from django.shortcuts import get_object_or_404, render
from .models import Product

def home_page_view (request):
    return render(request, 'shop/index.html')

def product_list_view(request):
    products = Product.objects.filter(is_active=True)
    return render(request, 'shop/product_list.html', {'products': products})


def shop_detail_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shop/product_detail.html', {'product': product})