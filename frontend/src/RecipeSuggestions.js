import React, { useState } from 'react';
import axios from 'axios';

const RecipeSuggestions = () => {
    const [ingredients, setIngredients] = useState('');
    const [goal, setGoal] = useState('improve nutrition');
    const [suggestions, setSuggestions] = useState([]);
    const [error, setError] = useState(null);

    const handleInputChange = (e) => {
        setIngredients(e.target.value);
    };

    const handleGoalChange = (e) => {
        setGoal(e.target.value);
    };

    const fetchSuggestions = async () => {
        try {
            const response = await axios.get('http://localhost:5001/api/suggest-alternatives', {
                params: {
                    ingredients: JSON.stringify(ingredients.split(',')),
                    goal: goal,
                },
            });
            setSuggestions(response.data.optimizedAlternatives || []);
            setError(null);
        } catch (err) {
            setError('Error al obtener sugerencias de recetas');
            setSuggestions([]);
        }
    };

    return (
        <div>
            <h2>Buscar Sugerencias de Recetas</h2>
            <div>
                <label>Ingredientes (separados por coma): </label>
                <input
                    type="text"
                    value={ingredients}
                    onChange={handleInputChange}
                    placeholder="Ejemplo: quinoa, garbanzos"
                />
            </div>
            <div>
                <label>Objetivo: </label>
                <select value={goal} onChange={handleGoalChange}>
                    <option value="improve nutrition">Mejorar Nutrición</option>
                    <option value="another goal">Otro Objetivo</option>
                </select>
            </div>
            <button onClick={fetchSuggestions}>Obtener Sugerencias</button>

            {error && <p style={{ color: 'red' }}>{error}</p>}

            <div>
                <h3>Recetas Sugeridas:</h3>
                {suggestions.length > 0 ? (
                    <ul>
                        {suggestions.map((recipe) => (
                            <li key={recipe.id}>
                                <h4>{recipe.title}</h4>
                                <img src={recipe.image} alt={recipe.title} width="100" />
                                <p>Ingredientes utilizados: {recipe.usedIngredientCount}</p>
                                <p>Ingredientes faltantes: {recipe.missedIngredientCount}</p>
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p>No hay sugerencias de recetas disponibles.</p>
                )}
            </div>
        </div>
    );
};

export default RecipeSuggestions;
