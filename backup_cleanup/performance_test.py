#!/usr/bin/env python
import os
import sys
import time
import logging
import random
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("performance_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Añadir directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar el sistema de caché inteligente
from src.features.external_api import get_spoonacular_client, get_recipe_cache

def run_performance_test(iterations=10):
    """
    Ejecuta una prueba de rendimiento para el sistema de caché inteligente.
    
    Args:
        iterations: Número de iteraciones a ejecutar
    """
    # Obtener instancia del caché y cliente
    cache = get_recipe_cache()
    client = get_spoonacular_client()
    
    # Opciones para pruebas
    fruits = ["fresa", "frambuesa", "arándano", "mora", "limón", "naranja", "mango", "piña"]
    gluten_options = [True, False]
    dairy_options = [True, False]
    
    # Estadísticas
    stats = {
        "from_cache": 0,
        "from_api": 0,
        "adapted": 0,
        "total_time": 0,
        "times": []
    }
    
    # Ejecutar pruebas
    logger.info(f"Iniciando prueba de rendimiento con {iterations} iteraciones")
    
    for i in range(iterations):
        # Elegir parámetros aleatorios
        fruit = random.choice(fruits)
        gluten_free = random.choice(gluten_options)
        dairy_free = random.choice(dairy_options)
        
        # Medir tiempo
        start_time = time.time()
        
        # Ejecutar consulta
        logger.info(f"Iteración {i+1}: gluten={gluten_free}, lactosa={dairy_free}, fruta={fruit}")
        recipe = client.get_complete_cheesecake_recipe(
            gluten_free=gluten_free,
            dairy_free=dairy_free,
            fruit=fruit
        )
        
        # Calcular tiempo
        elapsed = time.time() - start_time
        stats["times"].append(elapsed)
        stats["total_time"] += elapsed
        
        # Determinar fuente
        if recipe.get("properties", {}).get("de_default", False):
            stats["from_api"] += 1
            logger.info(f"Obtenida desde API en {elapsed:.2f} segundos")
        elif "adapted" in recipe:
            stats["adapted"] += 1
            logger.info(f"Adaptada desde caché en {elapsed:.2f} segundos")
        else:
            stats["from_cache"] += 1
            logger.info(f"Obtenida desde caché en {elapsed:.2f} segundos")
        
    # Calcular estadísticas
    avg_time = stats["total_time"] / iterations
    cache_percent = (stats["from_cache"] + stats["adapted"]) / iterations * 100
    
    # Mostrar resultados
    logger.info("=== RESULTADOS DE PRUEBA DE RENDIMIENTO ===")
    logger.info(f"Recetas obtenidas desde caché: {stats['from_cache']} ({stats['from_cache']/iterations*100:.1f}%)")
    logger.info(f"Recetas adaptadas: {stats['adapted']} ({stats['adapted']/iterations*100:.1f}%)")
    logger.info(f"Recetas obtenidas desde API: {stats['from_api']} ({stats['from_api']/iterations*100:.1f}%)")
    logger.info(f"Tiempo promedio: {avg_time:.2f} segundos")
    logger.info(f"Eficiencia de caché: {cache_percent:.1f}%")
    
    if stats["from_api"] > 0:
        api_times = [t for i, t in enumerate(stats["times"]) if i >= iterations - stats["from_api"]]
        avg_api_time = sum(api_times) / len(api_times) if api_times else 0
        logger.info(f"Tiempo promedio de API: {avg_api_time:.2f} segundos")
    
    if stats["from_cache"] + stats["adapted"] > 0:
        cache_times = [t for i, t in enumerate(stats["times"]) if i < stats["from_cache"] + stats["adapted"]]
        avg_cache_time = sum(cache_times) / len(cache_times) if cache_times else 0
        logger.info(f"Tiempo promedio de caché: {avg_cache_time:.2f} segundos")
        if stats["from_api"] > 0 and avg_api_time > 0:
            logger.info(f"Mejora de rendimiento: {avg_api_time/avg_cache_time:.1f}x más rápido")
    
    # Mostrar estadísticas finales del caché
    cache_stats = cache.get_stats()
    logger.info(f"Recetas totales en caché: {cache_stats['total_recipes']}")
    for type_name, count in cache_stats["recipe_types"].items():
        logger.info(f"  - {type_name}: {count} recetas")
        
if __name__ == "__main__":
    print(f"=== PRUEBA DE RENDIMIENTO DE CACHÉ INTELIGENTE ===")
    print(f"Fecha/hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Obtener número de iteraciones
    iterations = 20
    if len(sys.argv) > 1:
        try:
            iterations = int(sys.argv[1])
        except ValueError:
            pass
    
    # Ejecutar prueba
    run_performance_test(iterations=iterations) 