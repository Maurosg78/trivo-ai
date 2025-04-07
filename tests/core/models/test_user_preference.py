import pytest
from unittest.mock import Mock
from datetime import datetime

from src.core.models.user_preference import UserPreference


class TestUserPreferenceModel:
    """Pruebas para el modelo UserPreference."""

    def test_repr(self):
        """Prueba la representación en string del modelo."""
        preference = UserPreference(user_id=123)
        assert str(preference) == "<UserPreference for user 123>"

    def test_has_dietary_restrictions_true(self):
        """Prueba la propiedad has_dietary_restrictions cuando hay restricciones."""
        preference = UserPreference(dietary_restrictions=["vegetarian", "low_carb"])
        assert preference.has_dietary_restrictions is True

    def test_has_dietary_restrictions_false(self):
        """Prueba la propiedad has_dietary_restrictions cuando no hay restricciones."""
        preference1 = UserPreference(dietary_restrictions=[])
        assert preference1.has_dietary_restrictions is False
        
        preference2 = UserPreference(dietary_restrictions=None)
        assert preference2.has_dietary_restrictions is False

    def test_has_allergies_true(self):
        """Prueba la propiedad has_allergies cuando hay alergias."""
        preference = UserPreference(allergies=["peanuts", "gluten"])
        assert preference.has_allergies is True

    def test_has_allergies_false(self):
        """Prueba la propiedad has_allergies cuando no hay alergias."""
        preference1 = UserPreference(allergies=[])
        assert preference1.has_allergies is False
        
        preference2 = UserPreference(allergies=None)
        assert preference2.has_allergies is False

    def test_can_eat_ingredient_no_restrictions(self):
        """Prueba el método can_eat_ingredient sin restricciones."""
        preference = UserPreference(
            disliked_ingredients=[],
            allergies=[]
        )
        assert preference.can_eat_ingredient("tomato") is True
        assert preference.can_eat_ingredient("cheese") is True

    def test_can_eat_ingredient_with_dislikes(self):
        """Prueba el método can_eat_ingredient con ingredientes no deseados."""
        preference = UserPreference(
            disliked_ingredients=["mushroom", "olive"],
            allergies=[]
        )
        assert preference.can_eat_ingredient("tomato") is True
        assert preference.can_eat_ingredient("mushroom") is False
        assert preference.can_eat_ingredient("olive") is False

    def test_can_eat_ingredient_with_allergies(self):
        """Prueba el método can_eat_ingredient con alergias."""
        preference = UserPreference(
            disliked_ingredients=[],
            allergies=["peanut", "gluten"]
        )
        assert preference.can_eat_ingredient("tomato") is True
        assert preference.can_eat_ingredient("peanut butter") is False
        assert preference.can_eat_ingredient("whole wheat flour") is True  # No detecta "gluten" en el nombre

    def test_can_eat_ingredient_with_dislikes_and_allergies(self):
        """Prueba el método can_eat_ingredient con ingredientes no deseados y alergias."""
        preference = UserPreference(
            disliked_ingredients=["mushroom", "olive"],
            allergies=["peanut", "gluten"]
        )
        assert preference.can_eat_ingredient("tomato") is True
        assert preference.can_eat_ingredient("mushroom") is False
        assert preference.can_eat_ingredient("peanut butter") is False
        assert preference.can_eat_ingredient("olive oil") is True  # No detecta "olive" como substring 