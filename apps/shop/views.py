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
    if request.method == "POST":
                        
        name=request.POST['name'].strip()
        description=request.POST['description'].strip()
        price=request.POST['price'].strip()
        stock=request.POST['stock'].strip()
        is_active = 'is_active' in request.POST

        errors = {}
        if not name:
            errors['name'] = 'Наименование товара обязателено к заполнению.'
        elif len(name) < 6:
            errors['name'] = 'Наименование должно содержать минимум 6 символов.'
        elif len(name) > 200:
            errors['name'] = 'Наименование не должно превышать 200 символов.'

        if not description:
            errors['description'] = 'Описание товара обязателено к заполнению.'

        if not price:
            errors['price'] = 'Цена обязателена к заполнению.'
        else:
            try:
                if float(price) <= 0:
                    errors['price'] = 'Цена должна быть строго больше 0.'
            except ValueError:
                errors['price'] = 'Введите корректное числовое значение для цены.'

        if not stock:
            errors['stock'] = 'Количество товара обязателено к заполнению.'

        if errors:
            context = {
                'errors': errors,
                'name': name,
                'description': description,
                'price': price,
                'stock': stock,
                'is_active': is_active
            }
            return render(request, 'shop/pages/product_add.html', context)

        product = Product.objects.create(
            name=name,
            description=description,
            price=price,
            stock=stock,
            is_active=is_active
        )

        return redirect('shop:product_detail', product_id=product.id)

    return render(request, 'shop/pages/product_add.html')