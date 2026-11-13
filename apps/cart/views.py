from shop.models import Product
from django.contrib import messages
from django.contrib.auth.decorators import login_required
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

    if product.stock < 1:
        messages.error(request, 'Товара нет в наличии.')
        return redirect(request.META.get('HTTP_REFERER', 'cart:cart_detail'))

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart, product=product
    )
    if not created:
        if cart_item.quantity + 1 <= product.stock:
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, f'Количество «{product.name}» увеличено.')
        else:
            messages.warning(
                request, f'На складе доступно только {product.stock} шт.'
            )
    else:
        messages.success(request, f'Товар «{product.name}» добавлен в корзину.')

    return redirect('cart:cart_detail')


@login_required
@require_POST
def cart_update(request, item_id):
    cart_item = get_object_or_404(
        CartItem, id=item_id, cart__user=request.user
    )
    quantity = int(request.POST.get('quantity', 1))

    if quantity <= 0:
        cart_item.delete()
        messages.info(request, 'Товар удален из корзины.')
    elif quantity <= cart_item.product.stock:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, 'Количество обновлено.')
    else:
        cart_item.quantity = cart_item.product.stock
        cart_item.save()
        messages.warning(
            request,
            f'Максимально доступное количество: {cart_item.product.stock} шт.',
        )

    return redirect('cart:cart_detail')


@login_required
@require_POST
def cart_remove(request, item_id):
    cart_item = get_object_or_404(
        CartItem, id=item_id, cart__user=request.user
    )
    cart_item.delete()
    messages.info(request, 'Товар удален из корзины.')
    return redirect('cart:cart_detail')
