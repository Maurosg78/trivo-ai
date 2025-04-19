/**
 * Script para validar accesibilidad WCAG 2.1
 * Utiliza axe-core para realizar comprobaciones automáticas
 */

class AccessibilityChecker {
    constructor() {
        this.violations = [];
        this.passes = [];
        this.loadAxeCore();
    }

    /**
     * Carga la biblioteca axe-core desde CDN
     */
    loadAxeCore() {
        if (typeof axe === 'undefined') {
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.7.0/axe.min.js';
            script.integrity = 'sha512-hJhbR1zBBYTAg8FT1qqv5u4a9mPz5XDQxbFJaapLrMk2Xt8AOu/GkqS6RnUv5DF0OyYTZV5W0vC1HKJ2ei8/Vsg==';
            script.crossOrigin = 'anonymous';
            script.referrerPolicy = 'no-referrer';
            script.onload = () => {
                console.log('axe-core cargado correctamente');
            };
            document.head.appendChild(script);
        }
    }

    /**
     * Ejecuta las pruebas de accesibilidad en toda la página
     * @returns {Promise} Promesa que se resuelve con los resultados
     */
    async checkAccessibility(selector = document) {
        if (typeof axe === 'undefined') {
            console.error('axe-core no está cargado. Las pruebas no se pueden ejecutar.');
            return { error: 'axe-core no está cargado' };
        }

        try {
            const results = await axe.run(selector, {
                runOnly: {
                    type: 'tag',
                    values: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'best-practice']
                }
            });

            this.violations = results.violations;
            this.passes = results.passes;

            return results;
        } catch (error) {
            console.error('Error al ejecutar pruebas de accesibilidad:', error);
            return { error: error.message };
        }
    }

    /**
     * Obtiene un informe de violaciones críticas
     * @returns {Array} Violaciones críticas
     */
    getCriticalViolations() {
        return this.violations.filter(violation => 
            violation.impact === 'critical' || violation.impact === 'serious'
        );
    }

    /**
     * Genera un informe HTML con los resultados
     * @returns {String} HTML con el informe
     */
    generateReport() {
        let report = '<div class="accessibility-report">';
        
        if (this.violations.length === 0) {
            report += '<div class="alert alert-success"><i class="fas fa-check-circle me-2"></i> No se encontraron problemas de accesibilidad.</div>';
        } else {
            report += `<div class="alert alert-warning"><i class="fas fa-exclamation-triangle me-2"></i> Se encontraron ${this.violations.length} problemas de accesibilidad.</div>`;
            
            report += '<div class="accordion" id="a11yViolationsAccordion">';
            
            this.violations.forEach((violation, index) => {
                const id = `violation-${index}`;
                const impactClass = this.getImpactClass(violation.impact);
                
                report += `
                <div class="accordion-item">
                    <h2 class="accordion-header">
                        <button class="accordion-button collapsed ${impactClass}" type="button" data-bs-toggle="collapse" data-bs-target="#${id}" aria-expanded="false" aria-controls="${id}">
                            <span class="badge ${this.getImpactBadgeClass(violation.impact)} me-2">${violation.impact}</span>
                            ${violation.help}
                        </button>
                    </h2>
                    <div id="${id}" class="accordion-collapse collapse" data-bs-parent="#a11yViolationsAccordion">
                        <div class="accordion-body">
                            <p><strong>Descripción:</strong> ${violation.description}</p>
                            <p><strong>Impacto:</strong> ${violation.impact}</p>
                            <p><strong>Elementos afectados:</strong> ${violation.nodes.length}</p>
                            <p><strong>Criterio WCAG:</strong> ${violation.tags.filter(tag => tag.includes('wcag')).join(', ')}</p>
                            <h3 class="h6 mt-3">Elementos con problemas:</h3>
                            <ul class="list-group">
                                ${violation.nodes.map(node => `
                                    <li class="list-group-item">
                                        <code>${this.escapeHTML(node.html)}</code>
                                        <p class="mt-2 mb-0"><strong>Sugerencia:</strong> ${node.failureSummary}</p>
                                    </li>
                                `).join('')}
                            </ul>
                            <a href="${violation.helpUrl}" target="_blank" rel="noopener" class="btn btn-sm btn-info mt-3">
                                <i class="fas fa-info-circle"></i> Más información
                            </a>
                        </div>
                    </div>
                </div>`;
            });
            
            report += '</div>';
        }
        
        // Mostrar pruebas pasadas
        report += `<div class="mt-4">
            <h3>Pruebas superadas (${this.passes.length})</h3>
            <ul class="list-group">
                ${this.passes.map(pass => `
                    <li class="list-group-item list-group-item-success">
                        <i class="fas fa-check-circle me-2"></i> ${pass.help}
                    </li>
                `).join('')}
            </ul>
        </div>`;
        
        report += '</div>';
        return report;
    }

    /**
     * Obtiene la clase CSS para un nivel de impacto
     * @param {String} impact - Nivel de impacto (critical, serious, moderate, minor)
     * @returns {String} Clase CSS
     */
    getImpactClass(impact) {
        switch (impact) {
            case 'critical': return 'text-danger';
            case 'serious': return 'text-warning';
            case 'moderate': return 'text-primary';
            case 'minor': return 'text-secondary';
            default: return '';
        }
    }

    /**
     * Obtiene la clase CSS para un badge según el nivel de impacto
     * @param {String} impact - Nivel de impacto
     * @returns {String} Clase CSS para el badge
     */
    getImpactBadgeClass(impact) {
        switch (impact) {
            case 'critical': return 'bg-danger';
            case 'serious': return 'bg-warning';
            case 'moderate': return 'bg-primary';
            case 'minor': return 'bg-secondary';
            default: return 'bg-info';
        }
    }

    /**
     * Escapa HTML para mostrar código de forma segura
     * @param {String} html - HTML a escapar
     * @returns {String} HTML escapado
     */
    escapeHTML(html) {
        const div = document.createElement('div');
        div.textContent = html;
        return div.innerHTML;
    }

    /**
     * Muestra el informe en un modal
     */
    showReportModal() {
        // Crear modal si no existe
        let modal = document.getElementById('a11yReportModal');
        
        if (!modal) {
            modal = document.createElement('div');
            modal.className = 'modal fade';
            modal.id = 'a11yReportModal';
            modal.setAttribute('tabindex', '-1');
            modal.setAttribute('aria-labelledby', 'a11yReportModalLabel');
            modal.setAttribute('aria-hidden', 'true');
            
            modal.innerHTML = `
                <div class="modal-dialog modal-xl">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="a11yReportModalLabel">Informe de Accesibilidad</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
                        </div>
                        <div class="modal-body" id="a11yReportModalBody">
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                            <button type="button" class="btn btn-primary" id="a11yDownloadReport">
                                <i class="fas fa-download"></i> Descargar Informe
                            </button>
                        </div>
                    </div>
                </div>`;
            
            document.body.appendChild(modal);
            
            // Agregar evento para descargar informe
            document.getElementById('a11yDownloadReport').addEventListener('click', () => {
                this.downloadReport();
            });
        }
        
        // Actualizar contenido y mostrar
        document.getElementById('a11yReportModalBody').innerHTML = this.generateReport();
        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
    }

    /**
     * Descarga el informe como HTML
     */
    downloadReport() {
        const reportHTML = `
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Informe de Accesibilidad - TRIVO-AI</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
            <style>
                body { padding: 20px; }
                .accordion-button:not(.collapsed) { background-color: #f8f9fa; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Informe de Accesibilidad - TRIVO-AI</h1>
                <p>Fecha: ${new Date().toLocaleString()}</p>
                ${this.generateReport()}
            </div>
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>`;
        
        const blob = new Blob([reportHTML], { type: 'text/html' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `informe-accesibilidad-${new Date().toISOString().slice(0, 10)}.html`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

// Botón para activar comprobación de accesibilidad
document.addEventListener('DOMContentLoaded', function() {
    // Crear botón flotante para comprobar accesibilidad
    const checkButton = document.createElement('button');
    checkButton.id = 'checkAccessibilityBtn';
    checkButton.className = 'btn btn-primary position-fixed';
    checkButton.innerHTML = '<i class="fas fa-universal-access"></i> Comprobar Accesibilidad';
    checkButton.style.cssText = 'bottom: 20px; right: 20px; z-index: 1050;';
    checkButton.setAttribute('aria-label', 'Comprobar accesibilidad de la página');
    
    // Agregar botón al DOM
    document.body.appendChild(checkButton);
    
    // Evento de clic
    checkButton.addEventListener('click', async function() {
        const checker = new AccessibilityChecker();
        checkButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analizando...';
        checkButton.disabled = true;
        
        try {
            await checker.checkAccessibility();
            checker.showReportModal();
        } catch (error) {
            console.error('Error en comprobación de accesibilidad:', error);
            alert('Error al comprobar la accesibilidad: ' + error.message);
        } finally {
            checkButton.innerHTML = '<i class="fas fa-universal-access"></i> Comprobar Accesibilidad';
            checkButton.disabled = false;
        }
    });
}); 