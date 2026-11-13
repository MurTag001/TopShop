from shop.models import Product
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .models import Cart, CartItem


@login_required
def cart_detail(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart/pages/detail.html', {'cart': cart})


@login_required
@require_POST
def cart_add(request, product_id):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, id=product_id, is_active=True)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    next_url = request.META.get('HTTP_REFERER', 'shop:product_list')

    if product.stock < 1:
        msg = 'Товара нет в наличии.'
        if is_ajax:
            return JsonResponse({'status': 'error', 'message': msg}, status=400)
        messages.error(request, msg)
        return redirect(next_url)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, product=product
    )
    if not created:
        if cart_item.quantity + 1 <= product.stock:
            cart_item.quantity += 1
            cart_item.save()
            msg = f'Товар «{product.name}» добавлен (в корзине: {cart_item.quantity} шт.).'
            status = 'success'
        else:
            msg = f'На складе доступно только {product.stock} шт.'
            status = 'warning'
    else:
        msg = f'Товар «{product.name}» добавлен в корзину.'
        status = 'success'

    if is_ajax:
        return JsonResponse({
            'status': status,
            'message': msg,
            'total_quantity': cart.total_quantity,
        })

    getattr(messages, status)(request, msg)
    return redirect(next_url)


@login_required
@require_POST
def cart_update(request, item_id):
    cart_item = get_object_or_404(
        CartItem, id=item_id, cart__user=request.user
    )
    cart = cart_item.cart
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    try:
        quantity = int(request.POST.get('quantity', 1))
    except ValueError:
        quantity = 1

    deleted = False
    if quantity <= 0:
        cart_item.delete()
        deleted = True
        msg = 'Товар удален из корзины.'
        status = 'info'
        item_total = 0
    elif quantity <= cart_item.product.stock:
        cart_item.quantity = quantity
        cart_item.save()
        msg = 'Количество обновлено.'
        status = 'success'
        item_total = cart_item.total_price
    else:
        cart_item.quantity = cart_item.product.stock
        cart_item.save()
        msg = f'Максимально доступное количество: {cart_item.product.stock} шт.'
        status = 'warning'
        item_total = cart_item.total_price

    if is_ajax:
        return JsonResponse({
            'status': status,
            'message': msg,
            'deleted': deleted,
            'quantity': 0 if deleted else cart_item.quantity,
            'item_total': str(item_total),
            'cart_total_price': str(cart.total_price),
            'cart_total_quantity': cart.total_quantity,
        })

    getattr(messages, status)(request, msg)
    return redirect('cart:cart_detail')


@login_required
@require_POST
def cart_remove(request, item_id):
    cart_item = get_object_or_404(
        CartItem, id=item_id, cart__user=request.user
    )
    cart = cart_item.cart
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    cart_item.delete()
    msg = 'Товар удален из корзины.'

    if is_ajax:
        return JsonResponse({
            'status': 'info',
            'message': msg,
            'deleted': True,
            'cart_total_price': str(cart.total_price),
            'cart_total_quantity': cart.total_quantity,
        })

    messages.info(request, msg)
    return redirect('cart:cart_detail')