import sys
from pathlib import Path
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import get_settings
from src.core.models import Ingredient
from src.core.services.usda_service import USDAService

def main():
    # Configurar conexión a la base de datos
    settings = get_settings()
    engine = create_engine(str(settings.DATABASE_URL))
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Inicializar servicio USDA
    usda_service = USDAService()
    
    # Ingredientes básicos para pizza
    basic_ingredients = [
        "flour", "yeast", "salt", "sugar", "olive oil",
        "tomato", "mozzarella cheese", "parmesan cheese",
        "basil", "oregano", "garlic", "onion",
        "pepperoni", "mushroom", "bell pepper"
    ]
    
    db = SessionLocal()
    try:
        for ingredient_name in basic_ingredients:
            # Verificar si el ingrediente ya existe
            existing = db.query(Ingredient).filter(
                Ingredient.name.ilike(f"%{ingredient_name}%")
            ).first()
            
            if existing:
                print(f"Ingrediente '{ingredient_name}' ya existe")
                continue
            
            # Buscar en USDA API
            try:
                food_data = usda_service.search_food(ingredient_name)
                if not food_data:
                    print(f"No se encontró información para '{ingredient_name}'")
                    continue
                
                # Crear nuevo ingrediente
                nutrient_data = usda_service.get_nutrient_data(food_data[0]['fdcId'])
                new_ingredient = Ingredient(
                    name=ingredient_name,
                    description=food_data[0].get('description', ''),
                    category="basic",
                    usda_id=str(food_data[0]['fdcId']),
                    calories_per_100g=nutrient_data.get('calories', 0),
                    protein_per_100g=nutrient_data.get('protein', 0),
                    carbs_per_100g=nutrient_data.get('carbs', 0),
                    fat_per_100g=nutrient_data.get('fat', 0)
                )
                
                db.add(new_ingredient)
                print(f"Agregado ingrediente: {ingredient_name}")
                
            except Exception as e:
                print(f"Error procesando '{ingredient_name}': {e}")
                continue
        
        db.commit()
        print("Carga de ingredientes completada")
        
    except Exception as e:
        print(f"Error general: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main() 