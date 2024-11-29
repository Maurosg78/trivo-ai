/**
 * Filtro para buscar alternativas de ingredientes en base a restricciones.
 * 
 * @param {Array} ingredients - Lista de ingredientes originales.
 * @param {Object} restrictions - Restricciones (ej. sin gluten, vegano).
 * @param {Array} alternativesDB - Base de datos con alternativas.
 * @returns {Array} - Lista de ingredientes con alternativas sugeridas.
 */
function filterIngredients(ingredients, restrictions, alternativesDB) {
    const filteredIngredients = ingredients.map((ingredient) => {
        const alternative = alternativesDB.find((alt) => {
            return (
                alt.original === ingredient &&
                Object.entries(restrictions).every(([key, value]) => alt[key] === value)
            );
        });

        return alternative
            ? { original: ingredient, alternative: alternative.replacement }
            : { original: ingredient, alternative: null };
    });

    return filteredIngredients;
}

module.exports = filterIngredients;
