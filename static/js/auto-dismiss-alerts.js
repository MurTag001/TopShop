document.addEventListener('DOMContentLoaded', () => {
    const djangoMessages = document.querySelectorAll('.toast.auto-dismiss');
    
    djangoMessages.forEach(messageElement => {
        if (typeof bootstrap !== 'undefined') {
            const toast = new bootstrap.Toast(messageElement, { 
                delay: 4000,
                autohide: true 
            });
            toast.show();
        }
    });
});