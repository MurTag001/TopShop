function sendReaction(reviewId, isLike) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch("", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ 
            action: 'toggle_reaction', 
            review_id: reviewId, 
            is_like: isLike 
        })
    })
    .then(response => {
        if (response.status === 403) {
            alert('Пожалуйста, войдите в аккаунт, чтобы оценивать отзывы.');
            return;
        }
        return response.json();
    })
    .then(data => {
        if (data && data.status) {
            const reactionBlock = document.querySelector(`.reaction-buttons[data-review-id="${reviewId}"]`);
            if (!reactionBlock) return;

            const btnLike = reactionBlock.querySelector('.btn-like');
            const btnDislike = reactionBlock.querySelector('.btn-dislike');
            
            // Если кнопки найдены, обновляем их контент полностью, сохраняя иконки
            if (btnLike) {
                btnLike.innerHTML = `<i class="bi bi-hand-thumbs-up me-1"></i>${data.likes_count}`;
            }
            if (btnDislike) {
                btnDislike.innerHTML = `<i class="bi bi-hand-thumbs-down me-1"></i>${data.dislikes_count}`;
            }
            
            // Управление подсветкой активной реакции
            if (data.status === 'created' || data.status === 'updated') {
                if (isLike) {
                    if (btnLike) btnLike.classList.add('active');
                    if (btnDislike) btnDislike.classList.remove('active');
                } else {
                    if (btnDislike) btnDislike.classList.add('active');
                    if (btnLike) btnLike.classList.remove('active');
                }
            } else if (data.status === 'deleted') {
                if (btnLike) btnLike.classList.remove('active');
                if (btnDislike) btnDislike.classList.remove('active');
            }
        }
    })
    .catch(error => console.error('Ошибка при отправке реакции:', error));
}