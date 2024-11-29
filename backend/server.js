const express = require('express');
const axios = require('axios');
require('dotenv').config();
const cors = require('cors');

// Importar utilidades y datos
const filterIngredients = require('./utils/filters/ingredientFilter');
const alternatives = require('./utils/data/alternatives');

const app = express();

// Configuración de middleware
app.use(cors({
    origin: '*',
    methods: ['GET', 'POST'],
    allowedHeaders: ['Content-Type'],
}));
app.use(express.json()); // Necesario para procesar JSON en solicitudes POST

const USDA_API_KEY = process.env.USDA_API_KEY;

// Función para limpiar el input
const escapeInput = (input) => input.replace(/[&\/\\#,+()$~%.'":*?<>{}]/g, '');

// ** Función para obtener datos de Open Food Facts **
async function fetchFromOpenFoodFacts(query) {
    console.log(`Consultando Open Food Facts con: ${query}`);
    const isBarcode = /^\d{8,13}$/.test(query); // Verifica si es un código de barras
    try {
        const url = isBarcode
            ? `https://world.openfoodfacts.org/api/v0/product/${query}.json`
            : `https://world.openfoodfacts.org/cgi/search.pl?search_terms=${escapeInput(query)}&search_simple=1&action=process&json=1`;

        const response = await axios.get(url);
        if (isBarcode) {
            const product = response.data.product;
            if (product) return formatOpenFoodFactsProduct(product, query);
        } else if (response.data && response.data.products?.length > 0) {
            const product = response.data.products[0];
            return formatOpenFoodFactsProduct(product, query);
        }
    } catch (error) {
        console.error('Error en fetchFromOpenFoodFacts:', error.message);
    }
    return null;
}

function formatOpenFoodFactsProduct(product, query) {
    return {
        source: 'Open Food Facts',
        name: product.product_name || `Producto con código ${query}`,
        nutriments: cleanNutriments(product.nutriments || {}),
        ingredients: product.ingredients_text
            ? product.ingredients_text.split(',').map(i => i.trim())
            : ['Desconocido'],
    };
}

// ** Función para obtener datos de USDA **
async function fetchFromUSDA(query) {
    console.log(`Consultando USDA con: ${query}`);
    try {
        const response = await axios.get('https://api.nal.usda.gov/fdc/v1/foods/search', {
            params: { query, api_key: USDA_API_KEY },
        });

        if (response.data && response.data.foods?.length > 0) {
            const food = response.data.foods[0];
            return {
                source: 'USDA',
                name: food.description || query,
                nutriments: cleanNutriments(food.foodNutrients || {}),
                ingredients: food.ingredients?.split(',').map(i => i.trim()) || ['Desconocido'],
            };
        }
    } catch (error) {
        console.error('Error en fetchFromUSDA:', error.message);
    }
    return null;
}

// ** Función para limpiar y normalizar nutrientes **
function cleanNutriments(nutriments) {
    const clean = {};
    Object.entries(nutriments).forEach(([key, value]) => {
        if (!isNaN(value)) clean[key.toLowerCase()] = value;
    });
    return clean;
}

// ** Validar entradas **
function isValidInput(input) {
    return /^\d{8,13}$/.test(input) || input.trim().length >= 3;
}

// ** Combinar datos de ambas fuentes **
function combineData(data1, data2) {
    if (!data1 && !data2) return null;

    const combined = {
        sources: [],
        name: data1?.name || data2?.name || 'Producto desconocido',
        nutriments: {},
        ingredients: [],
    };

    [data1, data2].forEach(data => {
        if (data) {
            combined.sources.push(data.source);
            combined.ingredients = [...combined.ingredients, ...data.ingredients];
            Object.entries(data.nutriments).forEach(([key, value]) => {
                if (!combined.nutriments[key]) {
                    combined.nutriments[key] = { total: value, count: 1 };
                } else {
                    combined.nutriments[key].total += value;
                    combined.nutriments[key].count++;
                }
            });
        }
    });

    combined.nutriments = Object.fromEntries(
        Object.entries(combined.nutriments).map(([key, { total, count }]) => [key, total / count])
    );

    combined.ingredients = [...new Set(combined.ingredients)];
    return combined;
}

// ** Endpoint principal para obtener datos nutricionales **
app.get('/api/nutrition', async (req, res) => {
    const { input } = req.query;

    if (!input || !isValidInput(input)) {
        return res.status(400).json({
            success: false,
            message: "Entrada inválida. Proporcione un nombre, código de barras o UPC válido.",
        });
    }

    try {
        const openFoodFactsData = await fetchFromOpenFoodFacts(input);
        const usdaData = await fetchFromUSDA(openFoodFactsData?.name || input);

        const combinedData = combineData(openFoodFactsData, usdaData);

        if (!combinedData) {
            return res.status(404).json({
                success: false,
                message: "Producto no encontrado en ninguna base de datos.",
            });
        }

        res.json({ success: true, product: combinedData });
    } catch (error) {
        console.error("Error en el servidor:", error.message);
        res.status(500).json({ success: false, message: "Error interno del servidor." });
    }
});

// ** Endpoint para filtrar ingredientes y restricciones **
app.post('/api/ingredient-filter', (req, res) => {
    const { ingredients, restrictions } = req.body;

    if (!ingredients || !Array.isArray(ingredients)) {
        return res.status(400).json({ success: false, message: 'Se requiere una lista de ingredientes válida.' });
    }

    const filtered = filterIngredients(ingredients, restrictions || {}, alternatives);

    res.json({ success: true, filtered });
});

// Configurar el puerto del servidor
const PORT = 4000;
app.listen(PORT, () => {
    console.log(`Servidor corriendo en http://localhost:${PORT}`);
});
