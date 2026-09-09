from django.shortcuts import get_object_or_404, redirect, render
from .models import Product

def home_page_view (request):
    return render(request, 'shop/pages/index.html')

def product_list_view(request):
    products = Product.objects.filter(is_active=True)
    return render(request, 'shop/pages/product_list.html', {'products': products})


def shop_detail_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shop/pages/product_detail.html', {'product': product})


def product_add_view(request):
    if request.method == "GET":
        return render(request, 'shop/pages/product_add.html')

    elif request.method == "POST":
        
        is_active = 'is_active' in request.POST

        product = Product.objects.create(
            name=request.POST['name'],
            description=request.POST['description'],
            price=request.POST['price'],
            stock=request.POST['stock']
        )
        return redirect('shop:product_detail', product_id=product.id)