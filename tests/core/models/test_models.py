import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.models import Base, Ingredient, Recipe, RecipeIngredient, User, UserRole


class TestModels(unittest.TestCase):
    def setUp(self):
        # Crear motor de base de datos en memoria
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        
        # Crear un usuario para las pruebas
        self.test_user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hashedpassword",
            full_name="Test User",
            role=UserRole.USER,
            is_active=True
        )
        self.session.add(self.test_user)
        self.session.commit()

    def tearDown(self):
        self.session.close()

    def test_create_ingredient(self):
        """Prueba la creación de un ingrediente."""
        ingredient = Ingredient(
            name="Tomato",
            description="Fresh tomato",
            usda_id="12345",
            category="Vegetable",
            calories_per_100g=18,
            protein_per_100g=0.9,
            carbs_per_100g=3.9,
            fat_per_100g=0.2,
        )
        self.session.add(ingredient)
        self.session.commit()

        saved_ingredient = self.session.query(Ingredient).first()
        self.assertEqual(saved_ingredient.name, "Tomato")
        self.assertEqual(saved_ingredient.category, "Vegetable")

    def test_create_recipe(self):
        """Prueba la creación de una receta."""
        recipe = Recipe(
            name="Margherita Pizza",
            description="Classic Italian pizza",
            instructions="Mix ingredients and bake",
            preparation_time=20,
            cooking_time=15,
            servings=4,
            difficulty="medium",
            author_id=self.test_user.id,
            image_url="http://example.com/pizza.jpg",
        )
        self.session.add(recipe)
        self.session.commit()

        saved_recipe = self.session.query(Recipe).first()
        self.assertEqual(saved_recipe.name, "Margherita Pizza")
        self.assertEqual(saved_recipe.difficulty, "medium")

    def test_recipe_ingredient_relationship(self):
        """Prueba la relación entre recetas e ingredientes."""
        # Crear ingrediente
        ingredient = Ingredient(
            name="Tomato", 
            description="Fresh tomato", 
            category="Vegetable",
        )
        self.session.add(ingredient)

        # Crear receta
        recipe = Recipe(
            name="Margherita Pizza",
            description="Classic Italian pizza",
            instructions="Mix ingredients and bake",
            author_id=self.test_user.id,
        )
        self.session.add(recipe)
        self.session.commit()

        # Crear relación
        recipe_ingredient = RecipeIngredient(
            recipe=recipe, 
            ingredient=ingredient, 
            amount=200, 
            unit="g"
        )
        self.session.add(recipe_ingredient)
        self.session.commit()

        # Verificar relación
        saved_recipe = self.session.query(Recipe).first()
        self.assertEqual(len(saved_recipe.ingredients), 1)
        self.assertEqual(saved_recipe.ingredients[0].amount, 200)
        self.assertEqual(saved_recipe.ingredients[0].ingredient.name, "Tomato")


if __name__ == "__main__":
    unittest.main()
