from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from .models import Category, Product, Tag, Manufacturer
from .forms import ProductForm
from django.views.generic import TemplateView

class HomePageView(TemplateView):
    template_name =  'shop/pages/index.html'

def product_list_view(request):
    products = Product.objects.filter(is_active=True)
    return render(request, 'shop/pages/product_list.html', {'products': products})


def shop_detail_view(request, product_slug):
    if request.user.is_authenticated:
        condition = Q(slug=product_slug) & (Q(is_active=True) | Q(owner=request.user))
    else:
        condition = Q(slug=product_slug) & Q(is_active=True)
    
    product = get_object_or_404(Product, condition)
    return render(request, 'shop/pages/product_detail.html', {'product': product})


def category_products_view(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = category.products.filter(is_active=True)

    context = {
        'category': category,
        'products': products
    }
    return render(request, 'shop/pages/category_products.html', context)


def tag_products_view(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)
    products = tag.products.filter(is_active=True)

    context = {
        'tag': tag,
        'products': products
    }
    return render(request, 'shop/pages/tag_products.html', context)


def manufacturer_products_view(request, manufacturer_slug):
    manufacturer = get_object_or_404(Manufacturer, slug=manufacturer_slug)
    products = manufacturer.products.filter(is_active=True)

    context = {
        'manufacturer': manufacturer,
        'products': products
    }
    return render(request, 'shop/pages/manufacturer_products.html', context)


@login_required
def product_add_view(request):
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES or None)
        if form.is_valid():
            product = form.save(commit=False)
            product.owner = request.user

            m_name = form.cleaned_data.get('manufacturer_input')
            m_country = form.cleaned_data.get('manufacturer_country_input') or "Не указана"

            if m_name and m_name.strip():
                m_name = m_name.strip()
                m_slug = slugify(m_name.lower()) or "manufacturer-slug"

                manufacturer, created = Manufacturer.objects.get_or_create(
                    name=m_name,
                    defaults={
                        'country': m_country,
                        'slug': m_slug,
                        'description': f"Производитель {m_name}"
                    })
                product.manufacturer = manufacturer
            else:
                product.manufacturer = None 

            product.save()

            tag_names = form.cleaned_data.get('tags_input')

            for tag_name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                product.tags.add(tag)
            
            return redirect('shop:product_detail', product_slug=product.slug)
    else:
        form = ProductForm()

    return render(request, 'shop/pages/product_add.html', 
        {
            "form": form,
            "title": "Добавить позицию",
            "h1": "Новый товар",
            "submit_button_text": "Добавить",
        })

@login_required
def product_edit_view(request, product_slug):
    condition = Q(slug=product_slug) & (Q(is_active=True) | Q(owner=request.user))
    product = get_object_or_404(Product, condition)

    if request.user != product.owner:
        return render(request, 'shop/pages/not_allowed.html')
    
    extra_context = {
        "title": "Редактировать позицию",
        "h1": "Редактирование",
        "submit_button_text": "Сохранить",
    }

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()

            m_name = form.cleaned_data.get('manufacturer_input')
            m_country = form.cleaned_data.get('manufacturer_country_input') or "Не указана"

            if m_name and m_name.strip():
                m_name = m_name.strip()
                m_slug = slugify(m_name.lower()) or "manufacturer-slug"
                
                manufacturer, _ = Manufacturer.objects.get_or_create(
                    name=m_name,
                    defaults={'country': m_country, 'slug': m_slug}
                )
                product.manufacturer = manufacturer
            else:
                product.manufacturer = None
                
            product.save()

            product.tags.clear()
            tag_names = form.cleaned_data.get('tags_input')
            for tag_name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=tag_name)
                product.tags.add(tag)

            return redirect("shop:product_detail", product_slug=product.slug)
        return render(request, 'shop/pages/product_form.html', context={"form": form, **extra_context})
    else:
        initial_data = {}
        if product.manufacturer:
            initial_data['manufacturer_input'] = product.manufacturer.name
            initial_data['manufacturer_country_input'] = product.manufacturer.country
            
        initial_data['tags_input'] = ", ".join(tag.name for tag in product.tags.all())
        form = ProductForm(instance=product, initial=initial_data)

    return render(request, 'shop/pages/product_form.html', context={"form": form, **extra_context})


@login_required
def product_remove_view(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)

    if request.user != product.owner:
        return render(request, 'shop/pages/not_allowed.html')

    if request.method == "POST":
        product.delete()
        return redirect("shop:product_list")

    return render(request, 'shop/pages/product_remove_confirm.html', {'product': product})