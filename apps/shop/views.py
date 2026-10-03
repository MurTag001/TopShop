from django.contrib.auth.decorators import login_required
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


@login_required
def product_add_view(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.owner = request.user
            product.save() 
            
            return redirect('shop:product_detail', product_id=product.id)
    else:
        form = ProductForm()

    return render(request, 'shop/pages/product_add.html', 
        {
            "form": form,
            "title": "Добавить позицию",
            "h1": "Новый товар",
            "submit_button_text": "Добавить",
        })


def product_edit_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user != product.owner:
        return render(request, 'shop/pages/not_allowed.html')
    
    extra_context = {
        "title": "Редактировать позицию",
        "h1": "Редактирование",
        "submit_button_text": "Сохранить",
    }

    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)

        if form.is_valid():
            form.save()
            return redirect("shop:product_detail", product_id=product.id)
        return render(request, 'shop/pages/product_form.html', context={"form": form, **extra_context,})

    form = ProductForm(instance=product)
    return render(request, 'shop/pages/product_form.html', context={"form": form, **extra_context,})


def product_remove_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        product.delete()
        return redirect("shop:product_list")

    return render(request, 'shop/pages/product_remove_confirm.html', {'product': product})
