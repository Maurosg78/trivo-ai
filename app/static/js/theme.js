/**
 * TRIVO-AI Theme Manager
 * Controla la funcionalidad del modo oscuro y claro para la aplicación
 */

document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');
    const body = document.body;
    
    // Obtener preferencia guardada del tema
    const savedTheme = localStorage.getItem('trivoTheme');
    
    // Aplicar tema guardado o detectar preferencia del sistema
    if (savedTheme) {
        if (savedTheme === 'dark') {
            enableDarkMode();
        } else {
            enableLightMode();
        }
    } else {
        // Detectar preferencia del sistema
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            enableDarkMode();
        }
    }
    
    // Manejar clic en el botón de cambio de tema
    themeToggle.addEventListener('click', function() {
        if (body.classList.contains('dark-mode')) {
            enableLightMode();
        } else {
            enableDarkMode();
        }
    });
    
    // Añadir transición a elementos después de carga
    setTimeout(() => {
        document.querySelectorAll('.content-section, .card, .form-control, .btn').forEach(el => {
            el.classList.add('transition-fade');
        });
    }, 300);
    
    function enableDarkMode() {
        body.classList.add('dark-mode');
        themeIcon.classList.remove('fa-moon');
        themeIcon.classList.add('fa-sun');
        localStorage.setItem('trivoTheme', 'dark');
        
        // Notificar a otros scripts
        document.dispatchEvent(new CustomEvent('themeChanged', {
            detail: { theme: 'dark' }
        }));
    }
    
    function enableLightMode() {
        body.classList.remove('dark-mode');
        themeIcon.classList.remove('fa-sun');
        themeIcon.classList.add('fa-moon');
        localStorage.setItem('trivoTheme', 'light');
        
        // Notificar a otros scripts
        document.dispatchEvent(new CustomEvent('themeChanged', {
            detail: { theme: 'light' }
        }));
    }
}); 