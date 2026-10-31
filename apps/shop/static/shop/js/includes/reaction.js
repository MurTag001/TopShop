window.sendReaction = function(e, reviewId, isLike, clickedBtn) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';

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
            return null;
        }
        return response.json();
    })
    .then(data => {
        if (!data || !data.status) return;

        const reactionBlock = clickedBtn ? clickedBtn.closest('.reaction-buttons') : null;
        if (!reactionBlock) return;

        const btnLike = reactionBlock.querySelector('.btn-like');
        const btnDislike = reactionBlock.querySelector('.btn-dislike');

        if (btnLike) {
            const txt = btnLike.querySelector('.likes-count-text');
            if (txt) txt.textContent = data.likes_count;
        }
        if (btnDislike) {
            const txt = btnDislike.querySelector('.dislikes-count-text');
            if (txt) txt.textContent = data.dislikes_count;
        }

        const toggleClasses = (btn, isSuccess, activate) => {
            if (!btn) return;
            const activeClass = isSuccess ? 'btn-success' : 'btn-danger';
            const outlineClass = isSuccess ? 'btn-outline-success' : 'btn-outline-danger';
            
            if (activate) {
                btn.classList.remove(outlineClass);
                btn.classList.add(activeClass);
            } else {
                btn.classList.remove(activeClass);
                btn.classList.add(outlineClass);
            }
        };

        if (data.status === 'created' || data.status === 'updated') {
            toggleClasses(btnLike, true, isLike);
            toggleClasses(btnDislike, false, !isLike);
        } else if (data.status === 'deleted') {
            toggleClasses(btnLike, true, false);
            toggleClasses(btnDislike, false, false);
        }
    })
    .catch(error => console.error('Ошибка при отправке реакции:', error));
};