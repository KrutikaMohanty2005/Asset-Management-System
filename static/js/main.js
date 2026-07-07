document.addEventListener('DOMContentLoaded', () => {
    // Initialize Theme Toggler
    initTheme();
    
    // Auto-dismiss alert messages after 5 seconds
    const alerts = document.querySelectorAll('.alert-auto-dismiss');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            alert.style.transition = 'all 0.4s ease';
            setTimeout(() => {
                alert.remove();
            }, 400);
        }, 5000);
    });

    // Setup drag and drop indicators for file inputs
    setupDragAndDrop();
});

// Theme Management
function initTheme() {
    const themeBtn = document.getElementById('theme-toggle-btn');
    if (!themeBtn) return;
    
    const themeIcon = themeBtn.querySelector('i');
    const themeText = themeBtn.querySelector('span');
    
    // Read saved theme or default to dark
    const savedTheme = localStorage.getItem('ams-theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeUI(savedTheme, themeIcon, themeText);
    
    themeBtn.addEventListener('click', () => {
        const currentTheme = document.documentElement.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('ams-theme', newTheme);
        updateThemeUI(newTheme, themeIcon, themeText);
        
        // Dispatch custom event for Chart updates if they listen to it
        window.dispatchEvent(new CustomEvent('themechanged', { detail: { theme: newTheme } }));
    });
}

function updateThemeUI(theme, icon, text) {
    if (theme === 'light') {
        icon.className = 'fas fa-moon';
        text.textContent = 'Dark Mode';
    } else {
        icon.className = 'fas fa-sun';
        text.textContent = 'Light Mode';
    }
}

// Drag and drop interface decorators
function setupDragAndDrop() {
    const dropzone = document.querySelector('.file-upload-wrapper');
    const fileInput = document.querySelector('.file-upload-input');
    
    if (!dropzone || !fileInput) return;
    
    dropzone.addEventListener('click', () => {
        fileInput.click();
    });
    
    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            const fileName = fileInput.files[0].name;
            const sizeKB = (fileInput.files[0].size / 1024).toFixed(1);
            dropzone.querySelector('p').innerHTML = `<strong>Selected:</strong> ${fileName} (${sizeKB} KB)`;
            dropzone.querySelector('i').className = 'fas fa-file-check text-success';
        }
    });
    
    // Highlight drop area when dragging file over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropzone.style.borderColor = 'var(--accent-primary)';
            dropzone.style.background = 'rgba(255, 255, 255, 0.05)';
        }, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, (e) => {
            e.preventDefault();
            dropzone.style.borderColor = 'var(--border-color)';
            dropzone.style.background = 'var(--bg-input)';
        }, false);
    });
    
    dropzone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            fileInput.files = files;
            const event = new Event('change');
            fileInput.dispatchEvent(event);
        }
    });
}
