document.addEventListener('DOMContentLoaded', () => {
    // 1. Initialize syntax highlighting on loaded code blocks
    document.querySelectorAll('pre code').forEach((el) => {
        hljs.highlightElement(el);
    });

    // 2. Dark/Light Theme Toggle
    const themeToggleBtn = document.getElementById('theme-toggle');
    const themeIcon = document.getElementById('theme-icon');
    const htmlElement = document.documentElement;
    
    // Check local storage setting or default to dark
    const currentTheme = localStorage.getItem('theme') || 'dark';
    setTheme(currentTheme);

    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const newTheme = htmlElement.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark';
            setTheme(newTheme);
        });
    }

    function setTheme(theme) {
        htmlElement.setAttribute('data-bs-theme', theme);
        localStorage.setItem('theme', theme);
        
        if (theme === 'dark') {
            themeToggleBtn.classList.replace('btn-outline-dark', 'btn-outline-light');
            themeIcon.textContent = '🌙';
        } else {
            themeToggleBtn.classList.replace('btn-outline-light', 'btn-outline-dark');
            themeIcon.textContent = '☀️';
        }
    }

    // 3. Copy to clipboard functionality
    const copyBtns = document.querySelectorAll('.copy-btn');
    copyBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-target');
            const targetEl = document.getElementById(targetId);
            
            if (targetEl) {
                const textToCopy = targetEl.textContent;
                
                navigator.clipboard.writeText(textToCopy).then(() => {
                    const originalText = btn.textContent;
                    btn.textContent = 'Copié !';
                    btn.classList.add('btn-success');
                    btn.classList.remove('btn-outline-secondary');
                    
                    setTimeout(() => {
                        btn.textContent = originalText;
                        btn.classList.remove('btn-success');
                        btn.classList.add('btn-outline-secondary');
                    }, 2000);
                }).catch(err => {
                    console.error("Failed to copy text: ", err);
                    alert("Impossible de copier dans le presse-papier.");
                });
            }
        });
    });
});
