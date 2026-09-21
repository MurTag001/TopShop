from django.shortcuts import get_object_or_404, redirect, render
from .models import Product
from shop.forms import ProductForm

def home_page_view (request):
    return render(request, 'shop/pages/index.html')

def product_list_view(request):
    products = Product.objects.filter(is_active=True)
    return render(request, 'shop/pages/product_list.html', {'products': products})


def shop_detail_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shop/pages/product_detail.html', {'product': product})


def product_add_view(request):
    form = ProductForm(request.POST or None)
    if request.method == "POST":

        if form.is_valid():
            product = form.save()
            return redirect('shop:product_detail', product_id=product.id)
        
    return render(request, 'shop/pages/product_add.html', {"form": form})


def product_edit_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)

        if form.is_valid():
            form.save()
            return redirect("shop:product_detail", product_id=product.id)
        return render(request, 'shop/pages/product_edit.html', context={"form": form})

    form = ProductForm(instance=product)
    return render(request, 'shop/pages/product_edit.html', context={"form": form})
