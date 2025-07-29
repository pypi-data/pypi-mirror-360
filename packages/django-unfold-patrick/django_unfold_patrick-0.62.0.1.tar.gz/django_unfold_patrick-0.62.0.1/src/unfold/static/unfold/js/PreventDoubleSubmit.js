document.addEventListener('DOMContentLoaded', function() {
    console.log('Prevent double submit script loaded');
    const form = document.querySelector('#content-main form');
    const saveButtons = form.querySelectorAll('button[type="submit"]');
    
    let isSubmitting = false;
    
    if (form) {
        form.addEventListener('submit', function(e) {
            if (isSubmitting) {
                e.preventDefault();
                return false;
            }
            
            isSubmitting = true;
            
            // 버튼 비활성화
            saveButtons.forEach(button => {
                button.disabled = true;
                button.textContent = '저장 중...';
            });
            
            // 3초 후 다시 활성화 (네트워크 오류 대비)
            setTimeout(() => {
                isSubmitting = false;
                saveButtons.forEach(button => {
                    button.disabled = false;
                    button.textContent = button.name === '_save' ? '저장' : 
                                  button.name === '_continue' ? '저장 후 편집 계속' : '저장 후 새로 추가';
                });
            }, 3000);
        });
    }
});