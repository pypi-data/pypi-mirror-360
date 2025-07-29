document.addEventListener('DOMContentLoaded', function() {
    console.log('Prevent double submit script loaded');
    const form = document.querySelector('#content-main form');
    const submitRow = document.querySelector('#submit-row');
    const saveButtons = submitRow.querySelectorAll('button[type="submit"]');
    
    let isSubmitting = false;
    const originalTexts = new Map();
    
    saveButtons.forEach(button => {
        originalTexts.set(button, button.textContent);
    });
    
    if (form) {
        form.addEventListener('submit', function(e) {
            if (isSubmitting) {
                e.preventDefault();
                return false;
            }
            
            isSubmitting = true;
            
            saveButtons.forEach(button => {
                button.disabled = true;
                button.textContent = '...';
            });
            
            setTimeout(() => {
                isSubmitting = false;
                saveButtons.forEach(button => {
                    button.disabled = false;
                    button.textContent = originalTexts.get(button);
                });
            }, 3000);
        });
    }
});