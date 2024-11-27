const express = require('express');
const axios = require('axios');
require('dotenv').config();
const cors = require('cors');

const app = express();
const PORT = 4000;

// Configuración de CORS (actualizada para seguridad)
app.use(cors({
    origin: '*', // Cambia esto por el dominio del frontend en producción, ej: 'http://localhost:5500'
    methods: ['GET', 'POST'], // Métodos permitidos
    allowedHeaders: ['Content-Type'], // Headers permitidos
}));

// API Key de USDA
const USDA_API_KEY = process.env.USDA_API_KEY;

// Función para obtener datos de Open Food Facts
async function fetchFromOpenFoodFacts(barcode) {
    try {
        const response = await axios.get(`https://world.openfoodfacts.org/api/v0/product/${barcode}.json`);
        if (response.data.status === 1 && response.data.product) {
            const product = response.data.product;
            return {
                source: 'Open Food Facts',
                name: product.product_name || 'Unknown',
                nutriments: product.nutriments || {},
                ingredients: product.ingredients_text ? [product.ingredients_text] : [],
            };
        }
    } catch (error) {
        console.error('Error en Open Food Facts:', error.message);
    }
    return null;
}

// Función para obtener datos de USDA
async function fetchFromUSDA(query) {
    try {
        const response = await axios.get('https://api.nal.usda.gov/fdc/v1/foods/search', {
            params: {
                query: query,
                api_key: USDA_API_KEY,
            },
        });

        if (response.data.foods && response.data.foods.length > 0) {
            const food = response.data.foods[0]; // Tomar el primer resultado

            // Convertir nutrimentos en un objeto legible
            const nutrients = {};
            if (food.foodNutrients) {
                food.foodNutrients.forEach((n) => {
                    nutrients[n.nutrientName] = n.value || 'Not available';
                });
            }

            return {
                source: 'USDA',
                rawData: food, // Respuesta completa para uso adicional
                name: food.description || 'Unknown',
                nutriments: nutrients,
                ingredients: food.ingredients || ['Unknown'], // Ingredientes si están disponibles
            };
        }
    } catch (error) {
        console.error('Error en USDA:', error.message);
    }
    return null;
}

// Función para combinar datos de ambas fuentes
function combineData(data1, data2) {
    if (!data1 && !data2) return null;

    const combined = {
        sources: [],
        name: data1?.name || data2?.name || 'Unknown',
        nutriments: {},
        ingredients: [],
    };

    if (data1) {
        combined.sources.push(data1.source);
        combined.nutriments = { ...combined.nutriments, ...data1.nutriments };
        combined.ingredients = [...combined.ingredients, ...data1.ingredients];
    }

    if (data2) {
        combined.sources.push(data2.source);
        Object.keys(data2.nutriments).forEach((key) => {
            if (combined.nutriments[key] !== undefined) {
                combined.nutriments[key] = (combined.nutriments[key] + data2.nutriments[key]) / 2; // Promedio
            } else {
                combined.nutriments[key] = data2.nutriments[key];
            }
        });
        combined.ingredients = [...combined.ingredients, ...data2.ingredients];
    }

    // Limpiar ingredientes duplicados
    combined.ingredients = [...new Set(combined.ingredients)];

    // Incluir datos sin procesar si están disponibles
    if (data2?.rawData) {
        combined.usdaRawData = data2.rawData;
    }

    return combined;
}

// Endpoint principal
app.get('/api/nutrition/:input', async (req, res) => {
    const { input } = req.params;

    try {
        // Verificar si es un código de barras (8 a 13 dígitos numéricos)
        const isBarcode = /^\d{8,13}$/.test(input);

        let openFoodFactsData = null;
        let usdaData = null;

        if (isBarcode) {
            // Si es un código de barras, consultar ambas bases
            openFoodFactsData = await fetchFromOpenFoodFacts(input);
            usdaData = await fetchFromUSDA(input); // También se prueba con el código de barras
        } else {
            // Si es un nombre de producto, consultar USDA únicamente
            usdaData = await fetchFromUSDA(input);
        }

        // Combinar datos de ambas fuentes
        const combinedData = combineData(openFoodFactsData, usdaData);

        if (!combinedData) {
            return res.status(404).json({
                success: false,
                message: 'Producto no encontrado en ninguna base de datos.',
            });
        }

        return res.json({
            success: true,
            product: combinedData,
        });
    } catch (error) {
        console.error('Error al obtener datos nutricionales:', error.message);
        return res.status(500).json({
            success: false,
            message: 'Error al procesar la solicitud.',
        });
    }
});

// Iniciar servidor
app.listen(PORT, () => {
    console.log(`Servidor corriendo en http://localhost:${PORT}`);
});
