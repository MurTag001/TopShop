document.addEventListener('click', async (event) => {
    const button = event.target.closest('.favorite-btn');
    if (!button || button.tagName === 'A') return;

    event.preventDefault();

    const productId = button.dataset.id;
    const csrfTokenElement = button.querySelector('[name=csrfmiddlewaretoken]');
    
    if (!csrfTokenElement) {
        console.error('CSRF-токен не найден внутри кнопки!');
        return;
    }
    
    const csrfToken = csrfTokenElement.value;

    try {
        const response = await fetch(`/product/${productId}/favorite/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            }
        });

        if (!response.ok) throw new Error(`Ошибка сервера: ${response.status}`);

        const data = await response.json();

        if (data.status === 'ok') {
            const toastElement = document.getElementById('favoriteToast');
            const toastMessage = document.getElementById('toastMessage');
            
            if (data.is_favorite) {
                button.classList.add('is-favorite');
                
                // Уведомление на добавление
                if (toastElement && toastMessage) {
                    toastMessage.innerHTML = '❤️ Товар добавлен в избранное';
                    toastElement.className = 'toast fade align-items-center text-white bg-success border-0 rounded-3 shadow';
                }
            } else {
                button.classList.remove('is-favorite');
                
                // Уведомление на удаление
                if (toastElement && toastMessage) {
                    toastMessage.innerHTML = '🤍 Товар удален из избранного';
                    toastElement.className = 'toast fade align-items-center text-white bg-secondary border-0 rounded-3 shadow';
                }

                // Логика плавного удаления карточки (работает только на странице "Моё избранное")
                const favoriteWrapper = button.closest('.favorite-item-wrapper');
                if (favoriteWrapper) {
                    favoriteWrapper.style.transition = 'all 0.4s ease-in-out';
                    favoriteWrapper.style.opacity = '0';
                    favoriteWrapper.style.transform = 'scale(0.8)';
                    
                    setTimeout(() => {
                        favoriteWrapper.remove();
                        const countBadge = document.getElementById('favorites-count');
                        if (countBadge) {
                            const currentCount = parseInt(countBadge.innerText) - 1;
                            countBadge.innerText = currentCount;
                            if (currentCount === 0) location.reload();
                        }
                    }, 400);
                }
            }

            // Показываем Toast через встроенный API Bootstrap
            if (toastElement && typeof bootstrap !== 'undefined') {
                const toast = new bootstrap.Toast(toastElement, { delay: 4000 });
                toast.show();
            }
        }
    } catch (error) {
        console.error('Не удалось обработать клик на избранное:', error);
    }
});