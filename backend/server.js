const express = require('express');
const axios = require('axios');

const app = express();
const PORT = 4000;

// Función para buscar alternativas vegetales en línea
async function findPlantBasedAlternativesOnline(productNutriments) {
    try {
        // Realizar búsqueda en Open Food Facts por ingredientes vegetales
        const response = await axios.get('https://world.openfoodfacts.org/cgi/search.pl', {
            params: {
                search_terms: 'vegetables', // Ajuste del término de búsqueda
                json: true,
                page_size: 20 // Obtener hasta 20 resultados
            }
        });

        const products = response.data.products || [];

        if (products.length === 0) {
            console.log('No se encontraron productos en Open Food Facts.');
            return [];
        }

        // Filtrar productos con valores nutricionales completos
        const validProducts = products.filter(product => {
            const nutriments = product.nutriments || {};
            return nutriments.proteins_100g && nutriments.carbohydrates_100g && nutriments.fat_100g;
        });

        if (validProducts.length === 0) {
            console.log('No se encontraron productos con valores nutricionales completos.');
            return [];
        }

        // Calcular distancia ponderada entre nutrientes
        return validProducts.map(product => {
            const nutriments = product.nutriments;

            const score =
                2 * Math.abs((productNutriments.proteins || 0) - (nutriments.proteins_100g || 0)) +
                1 * Math.abs((productNutriments.carbohydrates || 0) - (nutriments.carbohydrates_100g || 0)) +
                1 * Math.abs((productNutriments.fat || 0) - (nutriments.fat_100g || 0));

            return {
                name: product.product_name || 'Unknown',
                nutriments,
                score
            };
        }).sort((a, b) => a.score - b.score) // Ordenar por menor distancia
            .slice(0, 5); // Limitar a las 5 mejores alternativas
    } catch (error) {
        console.error('Error fetching plant-based alternatives:', error.message);
        return [];
    }
}

// Función para calcular proporciones escaladas
function calculateProportions(alternatives, targetNutriments, targetWeight = 500) {
    if (alternatives.length === 0) {
        return [];
    }

    const proportions = alternatives.map(alt => {
        const nutriments = alt.nutriments;

        const scaleFactor = targetWeight / 100; // Basado en 100 g
        return {
            name: alt.name,
            amount: scaleFactor, // Cantidad en gramos
            contribution: {
                proteins: (nutriments.proteins_100g || 0) * scaleFactor,
                carbohydrates: (nutriments.carbohydrates_100g || 0) * scaleFactor,
                fat: (nutriments.fat_100g || 0) * scaleFactor
            }
        };
    });

    return proportions;
}

// Endpoint para obtener datos nutricionales por código de barras
app.get('/api/nutrition/:barcode', async (req, res) => {
    const { barcode } = req.params;

    try {
        // Llamar a Open Food Facts para obtener datos del producto
        const response = await axios.get(`https://world.openfoodfacts.org/api/v0/product/${barcode}.json`);
        const data = response.data;

        if (data.status === 1) {
            const productNutriments = data.product.nutriments;

            // Validar si el producto tiene valores nutricionales significativos
            if (
                (productNutriments.proteins || 0) === 0 &&
                (productNutriments.carbohydrates || 0) === 0 &&
                (productNutriments.fat || 0) === 0
            ) {
                return res.json({
                    success: true,
                    product: {
                        name: data.product.product_name || 'Unknown',
                        nutriments: productNutriments
                    },
                    message: "Este producto no tiene valores nutricionales significativos para buscar alternativas."
                });
            }

            console.log('Buscando alternativas vegetales...');
            const alternatives = await findPlantBasedAlternativesOnline(productNutriments);

            if (alternatives.length === 0) {
                return res.json({
                    success: true,
                    product: {
                        name: data.product.product_name || 'Unknown',
                        nutriments: productNutriments
                    },
                    message: "No se encontraron alternativas vegetales relevantes en Open Food Facts."
                });
            }

            console.log('Alternativas encontradas:', alternatives);

            const proportions = calculateProportions(alternatives, productNutriments, 500);
            console.log('Proporciones calculadas:', proportions);

            return res.json({
                success: true,
                product: {
                    name: data.product.product_name || 'Unknown',
                    nutriments: productNutriments
                },
                alternatives,
                proportions
            });
        } else {
            return res.status(404).json({ success: false, message: 'Product not found' });
        }
    } catch (error) {
        console.error('Error fetching product data:', error.message);
        return res.status(500).json({ success: false, message: 'Error fetching product data' });
    }
});

// Iniciar el servidor
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});

app.get('/api/nutrition/:barcode', async (req, res) => {
    const { barcode } = req.params;

    try {
        const response = await axios.get(`https://world.openfoodfacts.org/api/v0/product/${barcode}.json`);
        const data = response.data;

        if (data.status === 1) {
            const productNutriments = data.product.nutriments;

            if (
                (productNutriments.proteins || 0) === 0 &&
                (productNutriments.carbohydrates || 0) === 0 &&
                (productNutriments.fat || 0) === 0
            ) {
                console.log('Producto sin nutrientes significativos.');
                return res.json({
                    success: true,
                    product: {
                        name: data.product.product_name || 'Unknown',
                        nutriments: productNutriments
                    },
                    message: "Este producto no tiene valores nutricionales significativos para buscar alternativas."
                });
            }

            console.log('Producto recibido desde Open Food Facts:', data.product.product_name);
            console.log('Nutrientes del producto:', productNutriments);

            console.log('Buscando alternativas vegetales...');
            const alternatives = await findPlantBasedAlternativesOnline(productNutriments);

            if (alternatives.length === 0) {
                console.log('No se encontraron alternativas vegetales relevantes.');
                return res.json({
                    success: true,
                    product: {
                        name: data.product.product_name || 'Unknown',
                        nutriments: productNutriments
                    },
                    message: "No se encontraron alternativas vegetales relevantes en Open Food Facts."
                });
            }

            console.log('Alternativas encontradas:', alternatives);

            const proportions = calculateProportions(alternatives, productNutriments, 500);
            console.log('Proporciones calculadas:', proportions);

            return res.json({
                success: true,
                product: {
                    name: data.product.product_name || 'Unknown',
                    nutriments: productNutriments
                },
                alternatives,
                proportions
            });
        } else {
            console.log('Producto no encontrado en Open Food Facts.');
            return res.status(404).json({ success: false, message: 'Product not found' });
        }
    } catch (error) {
        console.error('Error fetching product data:', error.message);
        return res.status(500).json({ success: false, message: 'Error fetching product data' });
    }
});
