/**
 * Script para manejar el gráfico de historial de precios
 * Este archivo debe ser incluido después de cargar Chart.js
 */

function initPriceHistoryChart(chartData) {
    // Obtener el contexto del canvas
    const ctx = document.getElementById('priceChart').getContext('2d');
    
    // Configuración del gráfico
    const config = {
        type: 'line',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: {
                        display: true,
                        text: 'Fecha'
                    }
                },
                y: {
                    beginAtZero: false,
                    title: {
                        display: true,
                        text: 'Precio'
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Precio: ${context.raw}`;
                        }
                    }
                },
                legend: {
                    labels: {
                        font: {
                            size: 14
                        }
                    }
                }
            }
        }
    };
    
    // Crear el gráfico
    const myChart = new Chart(ctx, config);
    
    // Accesibilidad: Actualizar aria-label con resumen del gráfico
    const chartContainer = document.querySelector('.chart-container');
    if (chartContainer) {
        const summaryElement = document.getElementById('chartSummary');
        if (summaryElement) {
            chartContainer.setAttribute('aria-describedby', 'chartSummary');
        }
    }
    
    return myChart;
}

// Mejora para formulario: validación
document.addEventListener('DOMContentLoaded', function() {
    const updatePriceForm = document.getElementById('updatePriceForm');
    if (updatePriceForm) {
        updatePriceForm.addEventListener('submit', function(event) {
            if (!this.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            this.classList.add('was-validated');
        });
    }
}); 