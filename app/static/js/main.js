/**
 * PizzaAI - JavaScript principal
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicialización de tooltips de Bootstrap
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Funcionalidad para los mensajes de alerta
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        // Auto-cerrar alertas después de 5 segundos
        setTimeout(() => {
            const closeButton = alert.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    });

    // Mejora para la página de impresión
    const printButtons = document.querySelectorAll('[onclick="window.print()"]');
    printButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Añadir clase para estilos de impresión
            document.body.classList.add('printing');
            
            // Ejecutar la impresión
            window.print();
            
            // Eliminar clase después de la impresión
            setTimeout(() => {
                document.body.classList.remove('printing');
            }, 1000);
        });
    });

    // Funcionalidad para copiar contenido al portapapeles
    const copyButtons = document.querySelectorAll('.copy-to-clipboard');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const textToCopy = this.getAttribute('data-copy');
            
            if (textToCopy) {
                navigator.clipboard.writeText(textToCopy).then(() => {
                    // Cambiar el texto del botón temporalmente
                    const originalText = this.innerHTML;
                    this.innerHTML = '<i class="fas fa-check"></i> Copiado';
                    
                    setTimeout(() => {
                        this.innerHTML = originalText;
                    }, 2000);
                }).catch(err => {
                    console.error('Error al copiar al portapapeles:', err);
                });
            }
        });
    });

    // Animación para las tarjetas de características
    const featureCards = document.querySelectorAll('.card.shadow-sm');
    const animateOnScroll = () => {
        featureCards.forEach(card => {
            const cardTop = card.getBoundingClientRect().top;
            const triggerBottom = window.innerHeight * 0.8;
            
            if (cardTop < triggerBottom) {
                card.classList.add('animated');
            }
        });
    };
    
    // Ejecutar animación en scroll
    window.addEventListener('scroll', animateOnScroll);
    animateOnScroll(); // Ejecutar una vez al cargar la página
    
    // Toggle modo claro/oscuro
    const toggleThemeButton = document.getElementById('toggle-theme');
    if (toggleThemeButton) {
        toggleThemeButton.addEventListener('click', function() {
            document.body.classList.toggle('dark-theme');
            
            // Guardar preferencia en localStorage
            const isDarkTheme = document.body.classList.contains('dark-theme');
            localStorage.setItem('dark-theme', isDarkTheme);
            
            // Actualizar icono
            const themeIcon = this.querySelector('i');
            if (isDarkTheme) {
                themeIcon.classList.remove('fa-moon');
                themeIcon.classList.add('fa-sun');
            } else {
                themeIcon.classList.remove('fa-sun');
                themeIcon.classList.add('fa-moon');
            }
        });
        
        // Aplicar tema guardado
        const savedTheme = localStorage.getItem('dark-theme');
        if (savedTheme === 'true') {
            document.body.classList.add('dark-theme');
            const themeIcon = toggleThemeButton.querySelector('i');
            themeIcon.classList.remove('fa-moon');
            themeIcon.classList.add('fa-sun');
        }
    }
}); 