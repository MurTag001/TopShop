document.addEventListener('DOMContentLoaded', () => {
    const cartBadge = document.getElementById('cart-badge');
    const toastEl = document.getElementById('favoriteToast');
    const toastMessage = document.getElementById('toastMessage');

    // Универсальная функция показа всплывающего уведомления
    function showToast(message, status = 'success') {
        if (!toastEl || !toastMessage || !message) return;

        toastMessage.textContent = message;
        toastEl.classList.remove('bg-dark', 'bg-success', 'bg-warning', 'bg-danger', 'bg-info', 'text-dark', 'text-white');

        if (status === 'warning') {
            toastEl.classList.add('bg-warning', 'text-dark');
        } else if (status === 'error') {
            toastEl.classList.add('bg-danger', 'text-white');
        } else if (status === 'info') {
            toastEl.classList.add('bg-dark', 'text-white');
        } else {
            toastEl.classList.add('bg-success', 'text-white');
        }

        const toast = bootstrap.Toast.getOrCreateInstance(toastEl);
        toast.show();
    }

    // Универсальная функция обновления счетчика в шапке и итогов корзины
    function updateCartTotals(data) {
        if (cartBadge && data.cart_total_quantity !== undefined) {
            cartBadge.textContent = data.cart_total_quantity;
            if (data.cart_total_quantity > 0) {
                cartBadge.classList.remove('d-none');
            } else {
                cartBadge.classList.add('d-none');
            }
        }

        const totalQtyEl = document.getElementById('cart-total-quantity');
        const totalPriceEl = document.getElementById('cart-total-price');

        if (totalQtyEl && data.cart_total_quantity !== undefined) {
            totalQtyEl.textContent = data.cart_total_quantity;
        }
        if (totalPriceEl && data.cart_total_price !== undefined) {
            totalPriceEl.textContent = data.cart_total_price;
        }

        // Если товаров не осталось, скрываем таблицу и показываем плашку пустой корзины
        if (data.cart_total_quantity === 0) {
            const wrapper = document.getElementById('cart-content-wrapper');
            const emptyAlert = document.getElementById('empty-cart-alert');
            if (wrapper) wrapper.classList.add('d-none');
            if (emptyAlert) emptyAlert.classList.remove('d-none');
        }
    }

    // 1. Добавление товара в корзину из каталога
    document.querySelectorAll('.add-to-cart-form').forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const submitBtn = form.querySelector('button[type="submit"]');
            submitBtn.disabled = true;

            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value,
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                });

                if (response.redirected) {
                    window.location.href = response.url;
                    return;
                }

                const data = await response.json();
                updateCartTotals({ cart_total_quantity: data.total_quantity });
                showToast(data.message, data.status);
            } catch (error) {
                console.error('Ошибка при добавлении в корзину:', error);
            } finally {
                submitBtn.disabled = false;
            }
        });
    });

    // 2. Изменение количества на странице корзины
    document.querySelectorAll('.cart-update-form').forEach(form => {
        const input = form.querySelector('input[name="quantity"]');

        // Автоотправка при изменении значения в поле ввода
        if (input) {
            input.addEventListener('change', () => {
                form.dispatchEvent(new Event('submit', { cancelable: true }));
            });
        }

        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const row = form.closest('tr');
            const formData = new FormData(form);

            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value,
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                    body: formData,
                });

                const data = await response.json();

                if (data.deleted && row) {
                    row.remove();
                } else if (row) {
                    if (input && data.quantity) input.value = data.quantity;
                    const itemTotalEl = row.querySelector('.item-total-price');
                    if (itemTotalEl) itemTotalEl.textContent = data.item_total;
                }

                updateCartTotals(data);
                showToast(data.message, data.status);
            } catch (error) {
                console.error('Ошибка при обновлении корзины:', error);
            }
        });
    });

    // 3. Удаление товара на странице корзины
    document.querySelectorAll('.cart-remove-form').forEach(form => {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            const row = form.closest('tr');

            try {
                const response = await fetch(form.action, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value,
                        'X-Requested-With': 'XMLHttpRequest',
                    },
                });

                const data = await response.json();

                if (data.deleted && row) {
                    row.remove();
                }

                updateCartTotals(data);
                showToast(data.message, data.status);
            } catch (error) {
                console.error('Ошибка при удалении товара:', error);
            }
        });
    });
});
