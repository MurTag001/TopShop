document.addEventListener('DOMContentLoaded', function() {
    const reviewsContainer = document.getElementById('reviews-container');

    // Функция для динамического форматирования даты под часовой пояс пользователя
    const formatLocalDate = (isoString) => {
        if (!isoString) return '';
        const date = new Date(isoString);
        return date.toLocaleString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).replace(',', '');
    };

    // Вспомогательная функция для получения CSRF токена из куки (нужна для JSON fetch-запросов)
    const getCookie = (name) => {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    };

    // Автоматически форматируем все даты, которые уже были отрендерены сервером при загрузке
    document.querySelectorAll('.review-date, .comment-date').forEach(el => {
        const rawDate = el.getAttribute('data-raw-date');
        if (rawDate) {
            el.textContent = formatLocalDate(rawDate);
        }
    });

    // --- 1. ДОБАВЛЕНИЕ ОТЗЫВА (AJAX) ---
    const reviewForm = document.getElementById('ajax-review-form');
    if (reviewForm) {
        reviewForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            
            fetch(window.location.href, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => {
                return response.json().then(data => {
                    if (!response.ok) {
                        // Если статус ответа не 2xx (например, 400), принудительно уводим код в блок .catch
                        return Promise.reject({ status: response.status, data: data });
                    }
                    return data;
                });
            })
            .then(data => {
                if (data.status === 'success') {
                    const noReviewsText = document.getElementById('no-reviews-text');
                    if (noReviewsText) noReviewsText.remove();
                    
                    const template = document.getElementById('review-template');
                    const clone = template.content.cloneNode(true);
                    const newReviewCard = clone.querySelector('.review-card');
                    
                    newReviewCard.id = `review-card-${data.review_id}`;
                    newReviewCard.querySelector('.review-avatar').textContent = data.username.charAt(0).toUpperCase();
                    newReviewCard.querySelector('.review-username').textContent = data.username;
                    
                    newReviewCard.querySelector('.review-date').textContent = formatLocalDate(data.created_at);
                    newReviewCard.querySelector('.review-rating-text').textContent = data.rating;
                    newReviewCard.querySelector('.review-text').textContent = data.text;
                    
                    const reactionBlock = newReviewCard.querySelector('.reaction-buttons');
                    if (reactionBlock) {
                        reactionBlock.setAttribute('data-review-id', data.review_id);
                    }
                    
                    const commentList = newReviewCard.querySelector('.comments-list');
                    commentList.id = `comments-list-${data.review_id}`;
                    commentList.innerHTML = `<p class="text-muted small no-comments-text mb-0 py-2">К этому отзыву пока нет комментариев.</p>`;
                    
                    const commentForm = newReviewCard.querySelector('.ajax-comment-form');
                    if (commentForm) {
                        commentForm.setAttribute('data-review-id', data.review_id);
                        commentForm.querySelector('input[name="review_id"]').value = data.review_id;
                    }
                    
                    reviewsContainer.insertAdjacentElement('afterbegin', newReviewCard);
                    
                    const countEl = document.getElementById('reviews-count');
                    if (countEl) countEl.textContent = parseInt(countEl.textContent) + 1;
                    
                    reviewForm.reset();

                    // Блокируем повторную отправку отзыва (сработает ТОЛЬКО при реальном успехе)
                    const formContainer = reviewForm.parentElement;
                    if (formContainer) {
                        formContainer.innerHTML = `
                            <h4 class="fw-bold mb-4 text-dark">Оставить свой отзыв</h4>
                            <div class="alert alert-warning border-0 rounded-3 mb-0" style="background: #fef3c7; color: #b45309;">
                                <i class="bi bi-check-circle-fill me-2"></i> Вы уже оставили отзыв к этому товару. Спасибо за ваше мнение!
                            </div>
                        `;
                    }
                }
            })
            .catch(error => {
                console.error('Ошибка AJAX (Отзыв):', error);
                
                // ОБРАБОТКА ОШИБОК 400: Выводим ошибки валидации или предупреждение о дубликате
                if (error.data && error.data.errors) {
                    let errorMessages = [];
                    for (let field in error.data.errors) {
                        errorMessages.push(error.data.errors[field].join(' '));
                    }
                    alert(errorMessages.join('\n'));
                    
                    // Если бэкенд сообщил, что отзыв уже есть, то превентивно схлопываем форму на клиенте
                    if (JSON.stringify(error.data.errors).includes('уже оставили отзыв')) {
                        const formContainer = reviewForm.parentElement;
                        if (formContainer) {
                            formContainer.innerHTML = `
                                <h4 class="fw-bold mb-4 text-dark">Оставить свой отзыв</h4>
                                <div class="alert alert-warning border-0 rounded-3 mb-0" style="background: #fef3c7; color: #b45309;">
                                    <i class="bi bi-check-circle-fill me-2"></i> Вы уже оставили отзыв к этому товару. Спасибо за ваше мнение!
                                </div>
                            `;
                        }
                    }
                }
            });
        });
    }

    // --- 2. ДОБАВЛЕНИЕ КОММЕНТАРИЯ (AJAX Делегирование) ---
    if (reviewsContainer) {
        reviewsContainer.addEventListener('submit', function(e) {
            const targetForm = e.target.closest('.ajax-comment-form');
            if (!targetForm) return;
            
            e.preventDefault();
            const reviewId = targetForm.getAttribute('data-review-id');
            const formData = new FormData(targetForm);
            
            fetch(window.location.href, {
                method: 'POST',
                body: formData,
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    const commentsList = document.getElementById(`comments-list-${reviewId}`);
                    const noCommentsText = commentsList.querySelector('.no-comments-text');
                    if (noCommentsText) noCommentsText.remove();
                    
                    const template = document.getElementById('comment-template');
                    const clone = template.content.cloneNode(true);
                    
                    clone.querySelector('.comment-username').textContent = data.username;
                    clone.querySelector('.comment-date').textContent = formatLocalDate(data.created_at);
                    clone.querySelector('.comment-text').textContent = data.text;
                    
                    commentsList.appendChild(clone);
                    targetForm.reset();
                }
            })
            .catch(error => console.error('Ошибка AJAX (Комментарий):', error));
        });

        // --- 3. ОБРАБОТКА ЛАЙКОВ/ДИЗЛАЙКОВ (Новый JSON Делегированный обработчик) ---
        reviewsContainer.addEventListener('click', function(e) {
            const btn = e.target.closest('.btn-like, .btn-dislike');
            if (!btn) return;

            const reactionBlock = btn.closest('.reaction-buttons');
            const reviewId = reactionBlock.getAttribute('data-review-id');
            const isLike = btn.classList.contains('btn-like');

            // Отправляем чистый JSON запрос, как требует вьюха Django
            fetch(window.location.href, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({
                    action: 'toggle_reaction',
                    review_id: reviewId,
                    is_like: isLike
                })
            })
            .then(response => {
                if (!response.ok) throw new Error('Ошибка авторизации или неверные данные');
                return response.json();
            })
            .then(data => {
                // Динамически обновляем счетчики на кнопках конкретного отзыва
                const likesText = reactionBlock.querySelector('.likes-count-text') || reactionBlock.querySelector('.btn-like');
                const dislikesText = reactionBlock.querySelector('.dislikes-count-text') || reactionBlock.querySelector('.btn-dislike');
                
                if (likesText) likesText.textContent = data.likes_count;
                if (dislikesText) dislikesText.textContent = data.dislikes_count;

                // Опционально: здесь можно добавлять активные классы стилей для подсвечивания нажатой кнопки (data.status)
            })
            .catch(error => console.error('Ошибка обработки реакции:', error));
        });
    }
});