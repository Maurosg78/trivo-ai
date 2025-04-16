/**
 * Accessibility Preferences Panel
 * Script para manejar las preferencias de accesibilidad del usuario
 */

document.addEventListener('DOMContentLoaded', function() {
    const a11yToggleBtn = document.querySelector('.a11y-toggle-btn');
    const a11yPanel = document.getElementById('a11y-prefs-panel');
    const a11yCloseBtn = document.querySelector('.a11y-close-btn');
    const a11yResetBtn = document.querySelector('.a11y-reset-btn');
    const a11ySaveBtn = document.querySelector('.a11y-save-btn');
    const options = document.querySelectorAll('.a11y-option');
    
    // Opciones de accesibilidad
    const reduceMotionToggle = document.getElementById('reduce-motion-toggle');
    const enhanceFocusToggle = document.getElementById('enhance-focus-toggle');
    
    // Preferencias guardadas
    let preferences = {
        'text-size': 'default',
        'contrast': 'default',
        'letter-spacing': 'default',
        'line-height': 'default',
        'reduce-motion': false,
        'enhance-focus': false
    };
    
    // Cargar preferencias guardadas
    function loadSavedPreferences() {
        const savedPrefs = localStorage.getItem('a11y-preferences');
        if (savedPrefs) {
            preferences = JSON.parse(savedPrefs);
            applyPreferences(preferences, false);
            updateUI();
        }
    }
    
    // Aplicar preferencias de accesibilidad
    function applyPreferences(prefs, announce = true) {
        // Primero quitar todas las clases existentes
        document.body.classList.remove(
            'a11y-text-large', 'a11y-text-xlarge',
            'a11y-contrast-high', 'a11y-contrast-inverted',
            'a11y-letter-spacing-increased', 'a11y-letter-spacing-wide',
            'a11y-line-height-increased', 'a11y-line-height-wide',
            'a11y-reduce-motion', 'a11y-enhance-focus'
        );
        
        // Tamaño de texto
        if (prefs['text-size'] === 'large') {
            document.body.classList.add('a11y-text-large');
        } else if (prefs['text-size'] === 'xlarge') {
            document.body.classList.add('a11y-text-xlarge');
        }
        
        // Contraste
        if (prefs['contrast'] === 'high') {
            document.body.classList.add('a11y-contrast-high');
        } else if (prefs['contrast'] === 'inverted') {
            document.body.classList.add('a11y-contrast-inverted');
        }
        
        // Espaciado de letras
        if (prefs['letter-spacing'] === 'increased') {
            document.body.classList.add('a11y-letter-spacing-increased');
        } else if (prefs['letter-spacing'] === 'wide') {
            document.body.classList.add('a11y-letter-spacing-wide');
        }
        
        // Altura de línea
        if (prefs['line-height'] === 'increased') {
            document.body.classList.add('a11y-line-height-increased');
        } else if (prefs['line-height'] === 'wide') {
            document.body.classList.add('a11y-line-height-wide');
        }
        
        // Reducir movimiento
        if (prefs['reduce-motion']) {
            document.body.classList.add('a11y-reduce-motion');
        }
        
        // Mejorar indicadores de foco
        if (prefs['enhance-focus']) {
            document.body.classList.add('a11y-enhance-focus');
        }
        
        // Anunciar cambios para lectores de pantalla si es necesario
        if (announce) {
            announceChanges('Preferencias de accesibilidad aplicadas.');
        }
    }
    
    // Actualizar la interfaz para reflejar las preferencias actuales
    function updateUI() {
        // Actualizar botones de opciones
        options.forEach(option => {
            const feature = option.getAttribute('data-a11y-feature');
            const value = option.getAttribute('data-a11y-value');
            
            if (preferences[feature] === value) {
                option.setAttribute('aria-checked', 'true');
            } else {
                option.setAttribute('aria-checked', 'false');
            }
        });
        
        // Actualizar checkboxes
        reduceMotionToggle.checked = preferences['reduce-motion'];
        enhanceFocusToggle.checked = preferences['enhance-focus'];
    }
    
    // Guardar preferencias
    function savePreferences() {
        localStorage.setItem('a11y-preferences', JSON.stringify(preferences));
        announceChanges('Preferencias guardadas correctamente.');
    }
    
    // Restablecer preferencias
    function resetPreferences() {
        preferences = {
            'text-size': 'default',
            'contrast': 'default',
            'letter-spacing': 'default',
            'line-height': 'default',
            'reduce-motion': false,
            'enhance-focus': false
        };
        
        applyPreferences(preferences);
        updateUI();
        savePreferences();
        announceChanges('Preferencias restablecidas a valores predeterminados.');
    }
    
    // Anunciar cambios para lectores de pantalla
    function announceChanges(message) {
        const announcer = document.createElement('div');
        announcer.setAttribute('role', 'status');
        announcer.setAttribute('aria-live', 'polite');
        announcer.classList.add('visually-hidden');
        announcer.textContent = message;
        
        document.body.appendChild(announcer);
        
        // Remover después de que el lector lo haya anunciado
        setTimeout(() => {
            document.body.removeChild(announcer);
        }, 3000);
    }
    
    // Mostrar/ocultar panel
    if (a11yToggleBtn) {
        a11yToggleBtn.addEventListener('click', function() {
            const isExpanded = a11yPanel.classList.contains('active');
            a11yPanel.classList.toggle('active');
            a11yToggleBtn.setAttribute('aria-expanded', !isExpanded);
            
            if (!isExpanded) {
                // Si se abre el panel, enfocar el primer elemento dentro
                a11yPanel.querySelector('button, input, select').focus();
                announceChanges('Panel de preferencias de accesibilidad abierto');
            } else {
                announceChanges('Panel de preferencias de accesibilidad cerrado');
            }
        });
    }
    
    // Cerrar panel
    if (a11yCloseBtn) {
        a11yCloseBtn.addEventListener('click', function() {
            a11yPanel.classList.remove('active');
            a11yToggleBtn.setAttribute('aria-expanded', 'false');
            a11yToggleBtn.focus(); // Devolver el foco al botón toggle
            announceChanges('Panel de preferencias de accesibilidad cerrado');
        });
    }
    
    // Manejar opciones de botones
    options.forEach(option => {
        option.addEventListener('click', function() {
            const feature = this.getAttribute('data-a11y-feature');
            const value = this.getAttribute('data-a11y-value');
            
            // Actualizar valor en las preferencias
            preferences[feature] = value;
            
            // Actualizar UI
            const optionsGroup = this.parentElement;
            optionsGroup.querySelectorAll('.a11y-option').forEach(opt => {
                opt.setAttribute('aria-checked', 'false');
            });
            this.setAttribute('aria-checked', 'true');
            
            // Aplicar cambios
            applyPreferences(preferences);
        });
        
        // Soporte para navegación con teclado
        option.addEventListener('keydown', function(e) {
            if (e.key === ' ' || e.key === 'Enter') {
                e.preventDefault();
                this.click();
            }
        });
    });
    
    // Manejar checkboxes
    if (reduceMotionToggle) {
        reduceMotionToggle.addEventListener('change', function() {
            preferences['reduce-motion'] = this.checked;
            applyPreferences(preferences);
        });
    }
    
    if (enhanceFocusToggle) {
        enhanceFocusToggle.addEventListener('change', function() {
            preferences['enhance-focus'] = this.checked;
            applyPreferences(preferences);
        });
    }
    
    // Guardar preferencias
    if (a11ySaveBtn) {
        a11ySaveBtn.addEventListener('click', function() {
            savePreferences();
            a11yPanel.classList.remove('active');
            a11yToggleBtn.setAttribute('aria-expanded', 'false');
            a11yToggleBtn.focus();
        });
    }
    
    // Restablecer preferencias
    if (a11yResetBtn) {
        a11yResetBtn.addEventListener('click', function() {
            resetPreferences();
        });
    }
    
    // Cerrar panel al hacer clic fuera
    document.addEventListener('click', function(e) {
        if (a11yPanel.classList.contains('active') && 
            !a11yPanel.contains(e.target) && 
            e.target !== a11yToggleBtn) {
            a11yPanel.classList.remove('active');
            a11yToggleBtn.setAttribute('aria-expanded', 'false');
        }
    });
    
    // Cerrar panel con Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && a11yPanel.classList.contains('active')) {
            a11yPanel.classList.remove('active');
            a11yToggleBtn.setAttribute('aria-expanded', 'false');
            a11yToggleBtn.focus();
        }
    });
    
    // Cargar preferencias guardadas al inicio
    loadSavedPreferences();
}); 