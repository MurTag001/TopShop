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
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    const noReviewsText = document.getElementById('no-reviews-text');
                    if (noReviewsText) noReviewsText.remove();
                    
                    const template = document.getElementById('review-template');
                    const clone = template.content.cloneNode(true);
                    
                    clone.querySelector('.review-card').id = `review-card-${data.review_id}`;
                    clone.querySelector('.review-avatar').textContent = data.username.charAt(0).toUpperCase();
                    clone.querySelector('.review-username').textContent = data.username;
                    
                    // Форматируем ISO-дату на лету под клиента
                    clone.querySelector('.review-date').textContent = formatLocalDate(data.created_at);
                    clone.querySelector('.review-rating-text').textContent = data.rating;
                    clone.querySelector('.review-text').textContent = data.text;
                    
                    const commentList = clone.querySelector('.comments-list');
                    commentList.id = `comments-list-${data.review_id}`;
                    
                    const commentForm = clone.querySelector('.ajax-comment-form');
                    commentForm.setAttribute('data-review-id', data.review_id);
                    commentForm.querySelector('input[name="review_id"]').value = data.review_id;
                    commentForm.querySelector('input[name="csrfmiddlewaretoken"]').value = formData.get('csrfmiddlewaretoken');
                    
                    reviewsContainer.insertAdjacentElement('afterbegin', clone.querySelector('.review-card'));
                    
                    const countEl = document.getElementById('reviews-count');
                    countEl.textContent = parseInt(countEl.textContent) + 1;
                    
                    reviewForm.reset();
                }
            })
            .catch(error => console.error('Ошибка AJAX (Отзыв):', error));
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
                    
                    // Форматируем ISO-дату на лету под клиента
                    clone.querySelector('.comment-date').textContent = formatLocalDate(data.created_at);
                    clone.querySelector('.comment-text').textContent = data.text;
                    
                    commentsList.appendChild(clone);
                    targetForm.reset();
                }
            })
            .catch(error => console.error('Ошибка AJAX (Комментарий):', error));
        });
    }
});
