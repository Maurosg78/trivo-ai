/**
 * Accessibility Preferences Module
 * 
 * Este módulo gestiona las preferencias de accesibilidad del usuario,
 * permitiendo personalizar aspectos como tamaño de texto, contraste,
 * espaciado y animaciones.
 */

class AccessibilityPreferences {
    constructor() {
        this.preferences = {
            textSize: 'default',
            contrast: 'default',
            letterSpacing: 'default',
            lineHeight: 'default',
            reducedMotion: false,
            highFocus: false
        };
        
        // Cargar preferencias guardadas
        this.loadPreferences();
        
        // Inicializar panel y eventos
        this.initPanel();
        this.initToggleButton();
        this.applyPreferences();
    }
    
    /**
     * Inicializa el botón para mostrar/ocultar el panel
     */
    initToggleButton() {
        const toggleBtn = document.querySelector('.a11y-toggle-btn');
        if (!toggleBtn) return;
        
        toggleBtn.addEventListener('click', () => {
            this.togglePanel();
        });
        
        // Accesibilidad de teclado
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isPanelOpen()) {
                this.closePanel();
            }
        });
    }
    
    /**
     * Inicializa el panel y los eventos de las opciones
     */
    initPanel() {
        const panel = document.querySelector('.a11y-prefs-panel');
        if (!panel) return;
        
        // Inicializar cerrar panel
        const closeBtn = panel.querySelector('.btn-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                this.closePanel();
            });
        }
        
        // Inicializar opciones
        this.initOptions();
        
        // Inicializar botón para guardar
        const saveBtn = panel.querySelector('.a11y-prefs-save');
        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                this.savePreferences();
                this.closePanel();
            });
        }
        
        // Inicializar botón para restablecer
        const resetBtn = panel.querySelector('.a11y-prefs-reset');
        if (resetBtn) {
            resetBtn.addEventListener('click', () => {
                this.resetPreferences();
            });
        }
    }
    
    /**
     * Inicializa los eventos de las opciones de preferencias
     */
    initOptions() {
        // Tamaño de texto
        const textSizeOptions = document.querySelectorAll('[data-a11y-text-size]');
        textSizeOptions.forEach(option => {
            option.addEventListener('click', () => {
                this.selectOption(textSizeOptions, option);
                this.preferences.textSize = option.dataset.a11yTextSize;
                this.applyPreferences();
            });
        });
        
        // Contraste
        const contrastOptions = document.querySelectorAll('[data-a11y-contrast]');
        contrastOptions.forEach(option => {
            option.addEventListener('click', () => {
                this.selectOption(contrastOptions, option);
                this.preferences.contrast = option.dataset.a11yContrast;
                this.applyPreferences();
            });
        });
        
        // Espaciado de letras
        const letterSpacingOptions = document.querySelectorAll('[data-a11y-letter-spacing]');
        letterSpacingOptions.forEach(option => {
            option.addEventListener('click', () => {
                this.selectOption(letterSpacingOptions, option);
                this.preferences.letterSpacing = option.dataset.a11yLetterSpacing;
                this.applyPreferences();
            });
        });
        
        // Altura de línea
        const lineHeightOptions = document.querySelectorAll('[data-a11y-line-height]');
        lineHeightOptions.forEach(option => {
            option.addEventListener('click', () => {
                this.selectOption(lineHeightOptions, option);
                this.preferences.lineHeight = option.dataset.a11yLineHeight;
                this.applyPreferences();
            });
        });
        
        // Movimiento reducido
        const reducedMotionToggle = document.querySelector('[data-a11y-reduced-motion]');
        if (reducedMotionToggle) {
            reducedMotionToggle.addEventListener('click', () => {
                this.toggleOption(reducedMotionToggle);
                this.preferences.reducedMotion = reducedMotionToggle.classList.contains('selected');
                this.applyPreferences();
            });
        }
        
        // Indicadores de foco
        const highFocusToggle = document.querySelector('[data-a11y-high-focus]');
        if (highFocusToggle) {
            highFocusToggle.addEventListener('click', () => {
                this.toggleOption(highFocusToggle);
                this.preferences.highFocus = highFocusToggle.classList.contains('selected');
                this.applyPreferences();
            });
        }
    }
    
    /**
     * Selecciona una opción y deselecciona las demás del mismo grupo
     */
    selectOption(options, selectedOption) {
        options.forEach(opt => {
            opt.classList.remove('selected');
        });
        selectedOption.classList.add('selected');
    }
    
    /**
     * Alterna el estado de una opción (seleccionada/no seleccionada)
     */
    toggleOption(option) {
        option.classList.toggle('selected');
    }
    
    /**
     * Muestra u oculta el panel de preferencias
     */
    togglePanel() {
        const panel = document.querySelector('.a11y-prefs-panel');
        if (!panel) return;
        
        if (this.isPanelOpen()) {
            this.closePanel();
        } else {
            panel.style.display = 'flex';
            // Enfocar el primer elemento interactivo para accesibilidad
            setTimeout(() => {
                const firstFocusable = panel.querySelector('button, [tabindex="0"]');
                if (firstFocusable) {
                    firstFocusable.focus();
                }
            }, 100);
        }
    }
    
    /**
     * Cierra el panel de preferencias
     */
    closePanel() {
        const panel = document.querySelector('.a11y-prefs-panel');
        if (panel) {
            panel.style.display = 'none';
        }
    }
    
    /**
     * Verifica si el panel está abierto
     */
    isPanelOpen() {
        const panel = document.querySelector('.a11y-prefs-panel');
        return panel && panel.style.display === 'flex';
    }
    
    /**
     * Aplica las preferencias al documento
     */
    applyPreferences() {
        const body = document.body;
        
        // Restablecer todas las clases de accesibilidad
        body.classList.remove(
            'a11y-text-default', 'a11y-text-large', 'a11y-text-x-large',
            'a11y-contrast-default', 'a11y-contrast-high', 'a11y-contrast-inverted',
            'a11y-spacing-default', 'a11y-spacing-increased', 'a11y-spacing-wide',
            'a11y-lineheight-default', 'a11y-lineheight-increased', 'a11y-lineheight-wide',
            'a11y-motion-reduced', 'a11y-focus-high'
        );
        
        // Aplicar tamaño de texto
        if (this.preferences.textSize === 'large') {
            body.classList.add('a11y-text-large');
        } else if (this.preferences.textSize === 'x-large') {
            body.classList.add('a11y-text-x-large');
        }
        
        // Aplicar contraste
        if (this.preferences.contrast === 'high') {
            body.classList.add('a11y-contrast-high');
        } else if (this.preferences.contrast === 'inverted') {
            body.classList.add('a11y-contrast-inverted');
        }
        
        // Aplicar espaciado de letras
        if (this.preferences.letterSpacing === 'wide') {
            body.classList.add('a11y-spacing-wide');
        } else if (this.preferences.letterSpacing === 'wider') {
            body.classList.add('a11y-spacing-increased');
        }
        
        // Aplicar altura de línea
        if (this.preferences.lineHeight === 'spaced') {
            body.classList.add('a11y-lineheight-spaced');
        } else if (this.preferences.lineHeight === 'double') {
            body.classList.add('a11y-lineheight-double');
        }
        
        // Aplicar opciones adicionales
        if (this.preferences.reducedMotion) {
            body.classList.add('a11y-motion-reduced');
        }
        
        if (this.preferences.highFocus) {
            body.classList.add('a11y-focus-high');
        }
        
        // Marcar las opciones activas en el panel
        this.updateActiveOptions();
    }
    
    /**
     * Actualiza visualmente las opciones seleccionadas en el panel
     */
    updateActiveOptions() {
        // Actualizar tamaño de texto
        document.querySelectorAll('[data-a11y-text-size]').forEach(option => {
            if (option.dataset.a11yTextSize === this.preferences.textSize) {
                option.classList.add('selected');
            } else {
                option.classList.remove('selected');
            }
        });
        
        // Actualizar contraste
        document.querySelectorAll('[data-a11y-contrast]').forEach(option => {
            if (option.dataset.a11yContrast === this.preferences.contrast) {
                option.classList.add('selected');
            } else {
                option.classList.remove('selected');
            }
        });
        
        // Actualizar espaciado de letras
        document.querySelectorAll('[data-a11y-letter-spacing]').forEach(option => {
            if (option.dataset.a11yLetterSpacing === this.preferences.letterSpacing) {
                option.classList.add('selected');
            } else {
                option.classList.remove('selected');
            }
        });
        
        // Actualizar altura de línea
        document.querySelectorAll('[data-a11y-line-height]').forEach(option => {
            if (option.dataset.a11yLineHeight === this.preferences.lineHeight) {
                option.classList.add('selected');
            } else {
                option.classList.remove('selected');
            }
        });
        
        // Actualizar opciones adicionales
        const reducedMotionToggle = document.querySelector('[data-a11y-reduced-motion]');
        if (reducedMotionToggle) {
            if (this.preferences.reducedMotion) {
                reducedMotionToggle.classList.add('selected');
            } else {
                reducedMotionToggle.classList.remove('selected');
            }
        }
        
        const highFocusToggle = document.querySelector('[data-a11y-high-focus]');
        if (highFocusToggle) {
            if (this.preferences.highFocus) {
                highFocusToggle.classList.add('selected');
            } else {
                highFocusToggle.classList.remove('selected');
            }
        }
    }
    
    /**
     * Guarda las preferencias en localStorage
     */
    savePreferences() {
        try {
            localStorage.setItem('a11yPreferences', JSON.stringify(this.preferences));
        } catch (error) {
            console.error('Error al guardar preferencias de accesibilidad:', error);
        }
    }
    
    /**
     * Carga las preferencias desde localStorage
     */
    loadPreferences() {
        try {
            const savedPrefs = localStorage.getItem('a11yPreferences');
            if (savedPrefs) {
                this.preferences = { ...this.preferences, ...JSON.parse(savedPrefs) };
            }
        } catch (error) {
            console.error('Error al cargar preferencias de accesibilidad:', error);
        }
    }
    
    /**
     * Restablece las preferencias a los valores predeterminados
     */
    resetPreferences() {
        this.preferences = {
            textSize: 'default',
            contrast: 'default',
            letterSpacing: 'default',
            lineHeight: 'default',
            reducedMotion: false,
            highFocus: false
        };
        
        this.applyPreferences();
        this.savePreferences();
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.a11yPrefs = new AccessibilityPreferences();
}); 