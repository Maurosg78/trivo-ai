const express = require('express');
const axios = require('axios');
require('dotenv').config();
const cors = require('cors');

const app = express();
const PORT = 4000;

app.use(cors({
    origin: '*',
    methods: ['GET', 'POST'],
    allowedHeaders: ['Content-Type'],
}));

const USDA_API_KEY = process.env.USDA_API_KEY;

// Función para validar UPC
function isValidUPC(upc) {
    if (typeof upc !== "string" || upc.length !== 12 || !/^\d+$/.test(upc)) {
        return false;
    }

    let sum = 0;

    for (let i = 0; i < 11; i++) {
        const digit = parseInt(upc[i]);
        sum += i % 2 === 0 ? digit * 3 : digit;
    }

    const checkDigit = (10 - (sum % 10)) % 10;
    return checkDigit === parseInt(upc[11]);
}

// Función para consultar Open Food Facts
async function fetchFromOpenFoodFacts(barcode) {
    try {
        const url = `https://world.openfoodfacts.org/api/v0/product/${barcode}.json`;
        const response = await axios.get(url);
        const data = response.data;

        if (data.status === 1 && data.product) {
            const product = data.product;
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

// Función para consultar USDA
async function fetchFromUSDA(query) {
    try {
        const response = await axios.get('https://api.nal.usda.gov/fdc/v1/foods/search', {
            params: { query, api_key: USDA_API_KEY },
        });

        if (response.data.foods && response.data.foods.length > 0) {
            const food = response.data.foods[0];
            const nutrients = {};
            if (food.foodNutrients) {
                food.foodNutrients.forEach(n => {
                    nutrients[n.nutrientName] = n.value || 0;
                });
            }
            return {
                source: 'USDA',
                name: food.description || 'Unknown',
                nutriments: nutrients,
                ingredients: food.ingredients ? [food.ingredients] : ['Unknown'],
            };
        }
    } catch (error) {
        console.error('Error en USDA:', error.message);
    }
    return null;
}

// Función para combinar datos
function combineData(data1, data2) {
    const combined = {
        sources: [],
        name: data1?.name || data2?.name || 'Unknown',
        nutriments: {},
        ingredients: [],
    };

    [data1, data2].forEach((data) => {
        if (data) {
            combined.sources.push(data.source);
            combined.ingredients = [...combined.ingredients, ...data.ingredients];
            Object.entries(data.nutriments).forEach(([key, value]) => {
                if (combined.nutriments[key]) {
                    combined.nutriments[key] = (combined.nutriments[key] + value) / 2;
                } else {
                    combined.nutriments[key] = value;
                }
            });
        }
    });

    combined.sources = [...new Set(combined.sources)];
    combined.ingredients = [...new Set(combined.ingredients)];

    return combined;
}

// Endpoint principal
app.get('/api/nutrition', async (req, res) => {
    const input = req.query.input;

    if (!input || input.trim().length < 3) {
        return res.status(400).json({ success: false, message: 'Entrada inválida. Proporcione un nombre, código de barras o UPC válido.' });
    }

    try {
        let openFoodFactsData = null;
        let usdaData = null;

        // Si es un código de barras
        if (/^\d{8,13}$/.test(input)) {
            openFoodFactsData = await fetchFromOpenFoodFacts(input);
            if (openFoodFactsData && openFoodFactsData.name !== 'Unknown') {
                // Buscar en USDA usando el nombre obtenido de Open Food Facts
                usdaData = await fetchFromUSDA(openFoodFactsData.name);
            }
        } else if (/^\d{12}$/.test(input) && isValidUPC(input)) {
            // Si es un UPC válido, busca directamente en ambas fuentes
            openFoodFactsData = await fetchFromOpenFoodFacts(input);
            usdaData = await fetchFromUSDA(input);
        } else {
            // Si es un nombre, busca directamente en USDA
            usdaData = await fetchFromUSDA(input);
        }

        const combinedData = combineData(openFoodFactsData, usdaData);

        if (!combinedData) {
            return res.status(404).json({ success: false, message: 'Producto no encontrado en ninguna base de datos.' });
        }

        return res.json({ success: true, product: combinedData });
    } catch (error) {
        console.error('Error al obtener datos nutricionales:', error.message);
        return res.status(500).json({ success: false, message: 'Error interno del servidor.' });
    }
});

// Iniciar servidor
app.listen(PORT, () => {
    console.log(`Servidor corriendo en http://localhost:${PORT}`);
});
