from unittest.mock import Mock, patch

import pytest

from src.features.recommendations.recommendation_engine import (
    FoodItem,
    NutrientInfo,
    RecommendationEngine,
    UserPreferences,
)


@pytest.fixture
def mock_usda_service():
    with patch("src.features.recommendations.recommendation_engine.USDAService") as mock:
        service = Mock()
        mock.return_value = service
        yield service


@pytest.fixture
def mock_nutrition_analyzer():
    with patch("src.features.recommendations.recommendation_engine.NutritionAnalyzer") as mock:
        analyzer = Mock()
        mock.return_value = analyzer
        yield analyzer


@pytest.fixture
def sample_food_items():
    return [
        FoodItem(
            fdc_id=1,
            description="Pizza Margherita",
            nutrients=[
                NutrientInfo(id=1, name="protein", amount=12.0, unit="g"),
                NutrientInfo(id=2, name="carbohydrate", amount=30.0, unit="g"),
                NutrientInfo(id=3, name="fat", amount=10.0, unit="g"),
            ],
            serving_size=100,
            serving_unit="g",
        ),
        FoodItem(
            fdc_id=2,
            description="Pizza Pepperoni",
            nutrients=[
                NutrientInfo(id=1, name="protein", amount=15.0, unit="g"),
                NutrientInfo(id=2, name="carbohydrate", amount=28.0, unit="g"),
                NutrientInfo(id=3, name="fat", amount=14.0, unit="g"),
            ],
            serving_size=100,
            serving_unit="g",
        ),
    ]


@pytest.fixture
def sample_user_preferences():
    return UserPreferences(
        dietary_restrictions=["vegan"],
        nutritional_goals={"protein": 20.0, "carbohydrate": 30.0, "fat": 10.0},
        favorite_ingredients=["cheese", "tomato"],
        disliked_ingredients=["anchovies"],
    )


@pytest.mark.asyncio
async def test_get_recommendations(
    mock_usda_service, mock_nutrition_analyzer, sample_food_items, sample_user_preferences
):
    # Configurar mocks
    mock_usda_service.search_foods.return_value = sample_food_items
    mock_nutrition_analyzer.analyze_nutritional_profile.return_value = Mock(
        macronutrients={"protein": 15.0, "carbohydrate": 25.0, "fat": 12.0}
    )

    # Crear instancia y obtener recomendaciones
    engine = RecommendationEngine()
    recommendations = await engine.get_recommendations(sample_user_preferences, [], limit=2)

    # Verificar resultados
    assert len(recommendations) == 2
    assert all(isinstance(r.score, float) for r in recommendations)
    assert all(len(r.reasons) > 0 for r in recommendations)
    assert all(len(r.nutritional_benefits) > 0 for r in recommendations)

    # Verificar ordenamiento por score
    assert recommendations[0].score >= recommendations[1].score


@pytest.mark.asyncio
async def test_get_potential_foods(mock_usda_service, sample_food_items, sample_user_preferences):
    # Configurar mock
    mock_usda_service.search_foods.return_value = sample_food_items

    # Crear instancia y obtener alimentos potenciales
    engine = RecommendationEngine()
    foods = await engine._get_potential_foods(sample_user_preferences)

    # Verificar resultados
    assert len(foods) > 0
    assert all(isinstance(food, FoodItem) for food in foods)
    assert not any(
        restriction in food.description.lower()
        for food in foods
        for restriction in sample_user_preferences.dietary_restrictions
    )


def test_calculate_nutritional_score(sample_food_items):
    engine = RecommendationEngine()
    food = sample_food_items[0]
    nutritional_goals = {"protein": 15.0, "carbohydrate": 30.0, "fat": 10.0}

    score = engine._calculate_nutritional_score(food, nutritional_goals)
    assert 0 <= score <= 1


def test_calculate_ingredient_score(sample_food_items):
    engine = RecommendationEngine()
    food = sample_food_items[0]
    favorite_ingredients = ["cheese", "tomato"]

    score = engine._calculate_ingredient_score(food, favorite_ingredients)
    assert 0 <= score <= 1


def test_calculate_balance_score(mock_nutrition_analyzer, sample_food_items):
    # Configurar mock
    mock_nutrition_analyzer.analyze_nutritional_profile.return_value = Mock(
        macronutrients={"protein": 15.0, "carbohydrate": 25.0, "fat": 12.0}
    )

    engine = RecommendationEngine()
    food = sample_food_items[0]
    current_diet = [sample_food_items[1]]

    score = engine._calculate_balance_score(food, current_diet)
    assert 0 <= score <= 1


def test_generate_recommendation_reasons(sample_food_items):
    engine = RecommendationEngine()
    food = sample_food_items[0]
    score = 0.85

    reasons = engine._generate_recommendation_reasons(food, score)
    assert len(reasons) > 0
    assert all(isinstance(reason, str) for reason in reasons)
    assert "Excelente opción para tus objetivos" in reasons


def test_calculate_nutritional_benefits(mock_nutrition_analyzer, sample_food_items):
    # Configurar mock
    mock_nutrition_analyzer.analyze_nutritional_profile.return_value = Mock(
        macronutrients={"protein": 15.0, "carbohydrate": 25.0, "fat": 12.0}
    )

    engine = RecommendationEngine()
    food = sample_food_items[0]
    current_diet = [sample_food_items[1]]

    benefits = engine._calculate_nutritional_benefits(food, current_diet)
    assert isinstance(benefits, dict)
    assert all(isinstance(value, float) for value in benefits.values())
