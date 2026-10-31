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
                if (error.data && error.data.errors) {
                    let errorMessages = [];
                    for (let field in error.data.errors) {
                        errorMessages.push(error.data.errors[field].join(' '));
                    }
                    alert(errorMessages.join('\n'));
                    
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
                    if (!commentsList) return;
                    
                    const noCommentsText = commentsList.querySelector('.no-comments-text');
                    if (noCommentsText) noCommentsText.remove();
                    
                    const template = document.getElementById('comment-template');
                    if (!template) return;
                    
                    const clone = template.content.cloneNode(true);
                }
            })
            .catch(error => console.error('Ошибка AJAX (Комментарий):', error));
        });
    }

    // --- 3. ДЕЛЕГИРОВАНИЕ КЛИКОВ ДЛЯ РЕАКЦИЙ (ЛАЙКИ/ДИЗЛАЙКИ) ---
    if (reviewsContainer) {
        reviewsContainer.addEventListener('click', function(e) {
            const btnLike = e.target.closest('.btn-like');
            const btnDislike = e.target.closest('.btn-dislike');
            
            if (!btnLike && !btnDislike) return;

            const clickedBtn = btnLike || btnDislike;
            const reactionBlock = clickedBtn.closest('.reaction-buttons');
            if (!reactionBlock) return;

            const reviewId = reactionBlock.getAttribute('data-review-id');
            const isLike = !!btnLike;

            if (typeof window.sendReaction === 'function') {
                window.sendReaction(e, reviewId, isLike, clickedBtn);
            }
        });
    }
});