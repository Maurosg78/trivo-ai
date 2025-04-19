#!/usr/bin/env python
"""
Script de prueba del sistema PizzaAI

Este script verifica que los componentes clave del sistema estén funcionando 
correctamente, incluyendo la configuración y los módulos mock.
"""

import os
import sys
import json
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importar configuración
from config import OPENAI_API_KEY, DATA_DIR, LOG_LEVEL

# Intentar importar módulos reales primero
try:
    from app.llm_supervisor import LLMSupervisor
    supervisor_type = "REAL"
except ImportError:
    from app.mock_supervisor import MockLLMSupervisor as LLMSupervisor
    supervisor_type = "MOCK"

try:
    from trivo.features.nlp.language_processor import LanguageProcessor
    processor_type = "REAL (trivo)"
except ImportError:
    try:
        from src.features.nlp.language_processor import LanguageProcessor
        processor_type = "REAL (src)"
    except ImportError:
        from app.mock_language_processor import MockLanguageProcessor as LanguageProcessor
        processor_type = "MOCK"

def test_configuration():
    """Prueba que la configuración esté correctamente cargada"""
    print("\n=== Prueba de Configuración ===")
    print(f"DATA_DIR: {DATA_DIR}")
    print(f"LOG_LEVEL: {LOG_LEVEL}")
    
    # Verificar si OpenAI API está configurada
    if OPENAI_API_KEY and OPENAI_API_KEY != "sk-demo-key1234567890abcdef":
        print("OPENAI_API_KEY: ✓ (Configurada)")
    else:
        print("OPENAI_API_KEY: ✗ (No configurada correctamente)")
    
    # Verificar que los directorios existan
    if os.path.exists(DATA_DIR):
        print(f"Directorio de datos: ✓ (Existe en {DATA_DIR})")
    else:
        print(f"Directorio de datos: ✗ (No existe en {DATA_DIR})")

def test_supervisor():
    """Prueba el supervisor LLM"""
    print("\n=== Prueba de Supervisor LLM ===")
    print(f"Tipo de supervisor: {supervisor_type}")
    
    # Crear instancia del supervisor
    supervisor = LLMSupervisor()
    print(f"Modelo usado: {supervisor.model}")
    
    # Prueba de receta simple
    test_recipe = {
        "id": "test-123",
        "nombre": "Pizza de Prueba",
        "ingredientes": "300g harina, 175ml agua, 7g levadura, 5g sal",
        "instrucciones": "1. Mezclar todo\n2. Hornear"
    }
    
    # Revisar receta
    print("Revisando receta de prueba...")
    result = supervisor.review_recipe(test_recipe)
    print(f"Resultado: {'Aprobada' if result['approved'] else 'Rechazada'}")
    print(f"Feedback: {result['feedback'][:50]}...")
    
    # Prueba de retroalimentación
    print("Registrando retroalimentación de prueba...")
    feedback_result = supervisor.provide_feedback(
        "test-123",
        "clarity",
        "Instrucciones poco detalladas",
        "Añadir más detalle a los pasos",
        is_critical=False
    )
    print(f"Resultado: {'✓' if feedback_result else '✗'}")

def test_language_processor():
    """Prueba el procesador de lenguaje natural"""
    print("\n=== Prueba de Procesador de Lenguaje Natural ===")
    print(f"Tipo de procesador: {processor_type}")
    
    # Crear instancia del procesador
    processor = LanguageProcessor()
    
    # Prueba de procesamiento de texto
    print("Procesando solicitud de prueba...")
    text = "Quiero una pizza vegetariana con tomate y mozzarella"
    result = processor.process_request(text)
    
    print(f"ID de receta: {result.get('id', 'N/A')}")
    print(f"Nombre: {result.get('nombre', 'N/A')}")
    print(f"Éxito: {'✓' if result.get('success', False) else '✗'}")
    
    if 'query_analysis' in result:
        print(f"Análisis: {json.dumps(result['query_analysis'], indent=2, ensure_ascii=False)[:100]}...")

def main():
    """Función principal"""
    print("=== PRUEBA DEL SISTEMA PIZZAAI ===")
    print("Verificando componentes del sistema...")
    
    test_configuration()
    test_supervisor()
    test_language_processor()
    
    print("\n=== PRUEBA COMPLETA ===")

if __name__ == "__main__":
    main() 