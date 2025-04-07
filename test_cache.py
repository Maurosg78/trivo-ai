#!/usr/bin/env python
import os
import sys
import logging
import time
from datetime import datetime
from pprint import pprint

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Añadir directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar el sistema de caché inteligente
from src.features.external_api import get_spoonacular_client, get_recipe_cache

def test_recipe_cache():
    """Prueba el sistema de caché inteligente para recetas."""
    # Obtener instancia del caché y cliente
    cache = get_recipe_cache()
    client = get_spoonacular_client()
    
    # Mostrar estadísticas iniciales
    stats = cache.get_stats()
    print("=== Estadísticas iniciales del caché ===")
    pprint(stats)
    print()
    
    # Test 1: Obtener una receta de cheesecake básica
    print("=== Test 1: Obtener cheesecake básico ===")
    start_time = time.time()
    recipe1 = client.get_complete_cheesecake_recipe()
    elapsed1 = time.time() - start_time
    print(f"Nombre: {recipe1.get('name')}")
    print(f"Tiempo de ejecución: {elapsed1:.2f} segundos")
    print(f"Propiedades: {recipe1.get('properties')}")
    print(f"Ingredientes: {len(recipe1.get('ingredients', {}))} items")
    print()
    
    # Test 2: Obtener la misma receta de nuevo (debería usar caché)
    print("=== Test 2: Obtener el mismo cheesecake (debería usar caché) ===")
    start_time = time.time()
    recipe2 = client.get_complete_cheesecake_recipe()
    elapsed2 = time.time() - start_time
    print(f"Nombre: {recipe2.get('name')}")
    print(f"Tiempo de ejecución: {elapsed2:.2f} segundos")
    print(f"Mejora de rendimiento: {(elapsed1 / elapsed2) if elapsed2 > 0 else 'N/A'}x más rápido")
    print()
    
    # Test 3: Obtener cheesecake con fruta
    print("=== Test 3: Obtener cheesecake con frambuesa ===")
    start_time = time.time()
    recipe3 = client.get_complete_cheesecake_recipe(fruit="frambuesa")
    elapsed3 = time.time() - start_time
    print(f"Nombre: {recipe3.get('name')}")
    print(f"Tiempo de ejecución: {elapsed3:.2f} segundos")
    print(f"¿Adaptado de receta anterior? {recipe3.get('name') != recipe1.get('name')}")
    print()
    
    # Test 4: Obtener cheesecake sin gluten
    print("=== Test 4: Obtener cheesecake sin gluten ===")
    start_time = time.time()
    recipe4 = client.get_complete_cheesecake_recipe(gluten_free=True)
    elapsed4 = time.time() - start_time
    print(f"Nombre: {recipe4.get('name')}")
    print(f"Tiempo de ejecución: {elapsed4:.2f} segundos")
    print(f"Propiedades: {recipe4.get('properties')}")
    print()
    
    # Test 5: Obtener cheesecake sin lácteos
    print("=== Test 5: Obtener cheesecake sin lácteos ===")
    start_time = time.time()
    recipe5 = client.get_complete_cheesecake_recipe(dairy_free=True)
    elapsed5 = time.time() - start_time
    print(f"Nombre: {recipe5.get('name')}")
    print(f"Tiempo de ejecución: {elapsed5:.2f} segundos")
    print(f"Propiedades: {recipe5.get('properties')}")
    print()
    
    # Test 6: Obtener cheesecake con todo
    print("=== Test 6: Obtener cheesecake sin gluten, sin lácteos y con fruta ===")
    start_time = time.time()
    recipe6 = client.get_complete_cheesecake_recipe(gluten_free=True, dairy_free=True, fruit="arándanos")
    elapsed6 = time.time() - start_time
    print(f"Nombre: {recipe6.get('name')}")
    print(f"Tiempo de ejecución: {elapsed6:.2f} segundos")
    print(f"Propiedades: {recipe6.get('properties')}")
    print()
    
    # Mostrar estadísticas finales
    stats = cache.get_stats()
    print("=== Estadísticas finales del caché ===")
    pprint(stats)

def test_language_processor():
    """Prueba el procesador de lenguaje natural con el caché."""
    try:
        from src.features.nlp.language_processor import LanguageProcessor
        
        processor = LanguageProcessor()
        
        print("=== Test 1: Procesamiento de solicitud para cheesecake básico ===")
        request1 = "Quiero un cheesecake clásico"
        start_time = time.time()
        recipe1 = processor.process_request(request1)
        elapsed1 = time.time() - start_time
        print(f"Nombre: {recipe1.get('name')}")
        print(f"Tiempo de ejecución: {elapsed1:.2f} segundos")
        print()
        
        print("=== Test 2: Procesamiento de solicitud para cheesecake con fruta ===")
        request2 = "Me gustaría preparar un cheesecake de frambuesa"
        start_time = time.time()
        recipe2 = processor.process_request(request2)
        elapsed2 = time.time() - start_time
        print(f"Nombre: {recipe2.get('name')}")
        print(f"Tiempo de ejecución: {elapsed2:.2f} segundos")
        print()
        
        print("=== Test 3: Procesamiento de solicitud para cheesecake sin gluten con fruta ===")
        request3 = "Necesito un cheesecake sin gluten de arándanos"
        start_time = time.time()
        recipe3 = processor.process_request(request3)
        elapsed3 = time.time() - start_time
        print(f"Nombre: {recipe3.get('name')}")
        print(f"Tiempo de ejecución: {elapsed3:.2f} segundos")
        print()
        
    except ImportError:
        logger.error("No se pudo importar el procesador de lenguaje")

if __name__ == "__main__":
    print("=== PRUEBA DE SISTEMA DE CACHÉ INTELIGENTE ===")
    print(f"Fecha/hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if len(sys.argv) > 1 and sys.argv[1] == "clear":
        cache = get_recipe_cache()
        cache.clear_cache()
        print("Caché limpiado correctamente")
    elif len(sys.argv) > 1 and sys.argv[1] == "nlp":
        test_language_processor()
    else:
        test_recipe_cache() 