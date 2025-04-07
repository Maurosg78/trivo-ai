#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Base de conocimientos para recomendaciones contextuales.

Este módulo proporciona datos estructurados sobre ingredientes, técnicas,
hornos y recomendaciones específicas para diferentes tipos de masas y
restricciones dietéticas.
"""

from typing import Dict, List, Set, Any, Optional, Tuple
import json
import os

# Datos sobre técnicas de aireación y fermentación
AERATION_TECHNIQUES = {
    "con_levadura": {
        "agentes": ["levadura fresca", "levadura seca", "masa madre"],
        "beneficios": ["desarrollo de sabor", "producción de gas", "estructura aireada", "digestibilidad"],
        "tecnicas": ["prefermentación", "fermentación lenta en frío", "autolyse", "doble fermentación"],
        "mejoras": [
            "fermentación prolongada (12-24h) a baja temperatura (4°C)",
            "aumento de hidratación (+5-10%)",
            "incorporación de prefermentos (poolish, biga)",
            "uso de harinas de alta proteína (>12% proteína)"
        ]
    },
    "sin_levadura": {
        "agentes": ["polvo de hornear", "bicarbonato con ácido", "agua carbonatada", "clara de huevo"],
        "beneficios": ["rapidez", "consistencia", "control preciso", "menos dependencia de temperatura"],
        "tecnicas": ["amasado intensivo", "incorporación de aire", "batido", "laminado"],
        "mejoras": [
            "adición de agentes químicos (1-1.5% de la harina)",
            "sobrebatido para incorporar aire",
            "uso de grasas emulsionadas (mantequilla, aceite de oliva)",
            "adición de proteínas espumantes (clara de huevo, proteína de guisante)",
            "incorporación de hidrocoloides (goma xantana, guar) al 0.2-0.5% de la harina"
        ]
    }
}

# Datos sobre masas sin gluten
GLUTEN_FREE_SOLUTIONS = {
    "harinas": {
        "base": ["harina de arroz", "fécula de patata", "almidón de maíz", "almidón de tapioca"],
        "proteicas": ["harina de sorgo", "harina de mijo", "harina de alforfón", "harina de quinoa"],
        "fibra": ["harina de amaranto", "harina de teff", "copos de avena sin gluten", "harina de coco"]
    },
    "aglutinantes": {
        "agentes": ["goma xantana", "goma guar", "psyllium", "semillas de chía", "semillas de lino"],
        "proporcion": {
            "goma xantana": "0.2-0.5% del peso de la harina",
            "goma guar": "0.5-1% del peso de la harina",
            "psyllium": "2-3% del peso de la harina",
            "semillas de chía": "5-7% del peso de la harina hidratadas 1:3 con agua",
            "semillas de lino": "5-7% del peso de la harina hidratadas 1:3 con agua"
        }
    },
    "tecnicas": [
        "mayor hidratación (75-90% vs 60-70% tradicional)",
        "pregelatinización de parte del almidón",
        "técnica de masa líquida (batter technique)",
        "reposo más largo antes de hornear",
        "temperatura de horno ligeramente inferior (-10-15°C)"
    ],
    "mejoras_densidad": [
        "mezclar diferentes almidones (tapioca para elasticidad, patata para humedad)",
        "usar proteínas añadidas (huevo, proteína vegetal)",
        "incorporar grasas emulsionadas (aceite de oliva, mantequilla clarificada)",
        "doble horneado (primero solo la base, luego con ingredientes)",
        "añadir vinagre o ácido cítrico (1% del peso de la harina)"
    ]
}

# Datos sobre tipos de hornos y recomendaciones
OVEN_RECOMMENDATIONS = {
    "horno_pizza": {
        "nombre": "Horno de piedra/pizza",
        "temperatura": "400-450°C",
        "tiempo": "60-90 segundos",
        "ideal_para": ["masa napolitana", "masa fina", "cocción rápida"],
        "tecnicas": ["precalentar piedra completamente (>30 min)", "cocción directa sobre piedra", "llama alta"],
        "sugerencias": [
            "usar harina de semolina para deslizar la pizza",
            "masa muy hidratada (>65%)",
            "limitar los ingredientes húmedos",
            "manipulación mínima durante el estirado"
        ]
    },
    "horno_convencional": {
        "nombre": "Horno convencional",
        "temperatura": "200-250°C",
        "tiempo": "8-12 minutos",
        "ideal_para": ["masa americana", "masa gruesa", "focaccia", "pan pizza"],
        "tecnicas": ["precalentar completamente", "usar bandeja precalentada o piedra", "posición media-baja"],
        "sugerencias": [
            "usar bandeja oscura para mejor dorado de la base",
            "hidratación media (60-65%)",
            "posible cocción en dos fases (primero base, luego con ingredientes)"
        ]
    },
    "horno_conveccion": {
        "nombre": "Horno de convección",
        "temperatura": "180-220°C",
        "tiempo": "6-10 minutos",
        "ideal_para": ["masa sin gluten", "múltiples pizzas a la vez", "horneado uniforme"],
        "tecnicas": ["reducir la temperatura respecto a receta convencional (-20°C)", "rotación no necesaria", "mejor circulación de aire"],
        "sugerencias": [
            "supervisar atentamente por cocción más rápida",
            "posible deshidratación, mantener hidratada la superficie",
            "ideal para masas sin gluten por distribución uniforme del calor"
        ]
    },
    "sarten_horno": {
        "nombre": "Método mixto sartén+horno",
        "temperatura": "Fuego alto + 220-240°C",
        "tiempo": "2-3 min sartén + 5-7 min horno",
        "ideal_para": ["pizza casera sin equipo especializado", "base crujiente", "interior aireado"],
        "tecnicas": ["sartén de hierro o acero precalentada", "fuego alto para dorar base", "terminar en horno"],
        "sugerencias": [
            "cubrir sartén los primeros 30s para atrapar vapor",
            "asegurarse que la sartén es apta para horno",
            "funciona bien para masas con aceite de oliva"
        ]
    }
}

# Diccionario de sustituciones para restricciones dietéticas
DIETARY_SUBSTITUTIONS = {
    "sin_gluten": {
        "harina": ["mezcla de harina de arroz y almidón de tapioca (3:1)", "harina sin gluten comercial"],
        "harina de trigo": ["mezcla de harina de arroz y almidón de tapioca (3:1)", "harina sin gluten comercial"],
        "semolina": ["harina de maíz gruesa", "polenta fina"],
        "pan rallado": ["pan rallado sin gluten", "harina de garbanzos tostada"],
        "espesante": ["maicena", "fécula de patata", "goma xantana"],
        "aglutinante": ["psyllium hidratado", "semillas de chía hidratadas", "goma xantana"],
        "masa madre": ["masa madre de arroz", "masa madre sin gluten comercial"]
    },
    "sin_lactosa": {
        "leche": ["bebida vegetal (avena, almendra)", "leche sin lactosa"],
        "mantequilla": ["aceite de oliva", "mantequilla clarificada", "margarina vegetal"],
        "queso": ["queso sin lactosa", "queso vegano", "levadura nutricional"],
        "nata": ["nata vegetal", "leche de coco", "nata sin lactosa"],
        "yogur": ["yogur sin lactosa", "yogur de coco", "yogur de soja"]
    },
    "vegano": {
        "huevo": ["semillas de lino molidas con agua (1:3)", "aquafaba (agua de garbanzos)"],
        "miel": ["jarabe de agave", "sirope de arce", "azúcar moreno"],
        "leche": ["bebida vegetal (avena, soja, almendra)"],
        "mantequilla": ["aceite de oliva", "aceite de coco", "margarina vegetal"],
        "queso": ["queso vegano", "levadura nutricional", "tofu fermentado"],
        "proteína animal": ["proteína de guisante", "proteína de soja", "gluten vital de trigo"]
    }
}

# Sistema de caché para recomendaciones recientes
class RecommendationCache:
    """Caché para almacenar y recuperar recomendaciones recientes y frecuentes."""
    
    def __init__(self, cache_file=None):
        """Inicializa la caché de recomendaciones."""
        self.cache = {
            "by_issue": {},      # Problemas -> soluciones
            "by_restriction": {},  # Restricciones -> adaptaciones
            "by_technique": {},   # Técnicas -> mejoras
            "popular": []         # Recomendaciones más populares
        }
        self.cache_file = cache_file
        if cache_file and os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    self.cache = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                print(f"Error al cargar caché: {e}")
    
    def add_recommendation(self, category: str, key: str, recommendation: str):
        """
        Añade una recomendación a la caché.
        
        Args:
            category: Categoría de la recomendación (issue, restriction, technique)
            key: Clave específica (nombre del problema, restricción o técnica)
            recommendation: Texto de la recomendación
        """
        category_dict = self.cache.get(f"by_{category}", {})
        if key not in category_dict:
            category_dict[key] = []
        
        # Evitar duplicados
        if recommendation not in category_dict[key]:
            category_dict[key].append(recommendation)
        
        # Actualizar cache
        self.cache[f"by_{category}"] = category_dict
        
        # Actualizar populares
        if recommendation not in self.cache["popular"]:
            self.cache["popular"].append(recommendation)
            # Limitar a 100 entradas
            if len(self.cache["popular"]) > 100:
                self.cache["popular"] = self.cache["popular"][-100:]
        
        # Guardar si hay archivo configurado
        if self.cache_file:
            try:
                with open(self.cache_file, 'w') as f:
                    json.dump(self.cache, f, indent=2)
            except OSError as e:
                print(f"Error al guardar caché: {e}")
    
    def get_recommendations(self, category: str, key: str) -> List[str]:
        """
        Obtiene recomendaciones para una categoría y clave específicas.
        
        Args:
            category: Categoría de la recomendación (issue, restriction, technique)
            key: Clave específica (nombre del problema, restricción o técnica)
            
        Returns:
            Lista de recomendaciones
        """
        category_dict = self.cache.get(f"by_{category}", {})
        return category_dict.get(key, [])
    
    def get_popular_recommendations(self, limit: int = 10) -> List[str]:
        """
        Obtiene las recomendaciones más populares.
        
        Args:
            limit: Número máximo de recomendaciones a devolver
            
        Returns:
            Lista de recomendaciones populares
        """
        return self.cache.get("popular", [])[:limit]


# Función para generar recomendaciones contextuales
def get_contextual_recommendation(
    issue: str,
    recipe_type: str,
    has_gluten: bool = True,
    has_yeast: bool = True,
    dietary_restrictions: List[str] = None,
    oven_type: str = "horno_convencional",
    cache: Optional[RecommendationCache] = None
) -> Dict[str, Any]:
    """
    Genera recomendaciones contextuales basadas en el problema y contexto.
    
    Args:
        issue: Problema o aspecto a mejorar
        recipe_type: Tipo de receta (pizza, pan, etc.)
        has_gluten: Si la receta contiene gluten
        has_yeast: Si la receta usa levadura
        dietary_restrictions: Lista de restricciones dietéticas
        oven_type: Tipo de horno utilizado
        cache: Caché de recomendaciones (opcional)
        
    Returns:
        Diccionario con recomendaciones contextualizadas
    """
    if dietary_restrictions is None:
        dietary_restrictions = []
    
    # Inicializar respuesta
    response = {
        "issue": issue,
        "recommendations": [],
        "substitutions": [],
        "techniques": [],
        "equipment": []
    }
    
    # Comprobar caché primero
    if cache:
        cached_recommendations = cache.get_recommendations("issue", issue)
        if cached_recommendations:
            response["recommendations"].extend(cached_recommendations)
    
    # Recomendaciones específicas según problema
    if issue == "densidad_alta":
        if not has_gluten:
            # Recomendaciones para masas sin gluten densas
            response["recommendations"].extend([
                "Incrementar la hidratación al 80-90% del peso de la harina",
                "Añadir psyllium hidratado (2-3% del peso de la harina)",
                "Incluir proteína de clara de huevo para mejorar estructura"
            ])
            response["techniques"].extend(GLUTEN_FREE_SOLUTIONS["mejoras_densidad"])
        elif has_yeast:
            # Recomendaciones para masas con gluten y levadura densas
            response["recommendations"].extend([
                "Prolongar fermentación a 18-24 horas en refrigerador",
                "Aumentar hidratación en 5-10%",
                "Utilizar técnica de pliegues cada 30 minutos durante la primera hora"
            ])
        else:
            # Recomendaciones para masas con gluten sin levadura
            response["recommendations"].extend([
                "Incorporar más aire durante el amasado con técnica de palmeo",
                "Añadir bicarbonato con ácido cítrico o vinagre",
                "Utilizar mayor proporción de grasa para facilitar laminado"
            ])
    
    elif issue == "falta_fermentacion":
        if has_yeast:
            # Mejorar fermentación con levadura
            response["recommendations"].extend([
                "Extender tiempo de fermentación a temperatura ambiente (2-3 horas)",
                "Utilizar prefermentos como poolish (50% harina fermentada 12-16h)",
                "Combinar fermentación ambiente con refrigerada (24-48h)"
            ])
        else:
            # Alternativas si no hay levadura
            response["recommendations"].extend([
                f"Incorporar agentes de levado químicos como {', '.join(AERATION_TECHNIQUES['sin_levadura']['agentes'][:2])}",
                "Usar técnicas de aireación manual intensiva durante el amasado",
                "Considerar agua carbonatada para incorporar burbujas"
            ])
            response["techniques"].extend(AERATION_TECHNIQUES["sin_levadura"]["mejoras"])
    
    elif issue == "coccion_inadecuada":
        # Recomendaciones específicas para el tipo de horno
        if oven_type in OVEN_RECOMMENDATIONS:
            oven_info = OVEN_RECOMMENDATIONS[oven_type]
            response["recommendations"].append(
                f"Para {recipe_type} en {oven_info['nombre']}, usar temperatura {oven_info['temperatura']} durante {oven_info['tiempo']}"
            )
            response["techniques"].extend(oven_info["tecnicas"])
            response["equipment"].append(oven_info["nombre"])
        
        # Consideraciones para sin gluten
        if not has_gluten:
            response["recommendations"].append(
                "Las masas sin gluten necesitan temperatura ligeramente más baja (-15°C) y tiempo más largo (+20%)"
            )
    
    # Procesar restricciones dietéticas
    for restriction in dietary_restrictions:
        if restriction in DIETARY_SUBSTITUTIONS:
            for ingredient, substitutes in DIETARY_SUBSTITUTIONS[restriction].items():
                # No añadir sustituciones para harina si ya estamos en sin_gluten
                if restriction == "sin_gluten" and not has_gluten and ingredient in ["harina", "harina de trigo"]:
                    continue
                
                response["substitutions"].append({
                    "original": ingredient,
                    "alternatives": substitutes,
                    "restriction": restriction
                })
    
    # Añadir a caché si se proporciona
    if cache and response["recommendations"]:
        for rec in response["recommendations"]:
            cache.add_recommendation("issue", issue, rec)
    
    return response


# Función para verificar coherencia de recomendaciones
def verify_recommendation_coherence(
    recommendations: Dict[str, Any],
    recipe_context: Dict[str, Any]
) -> Tuple[bool, List[str]]:
    """
    Verifica que las recomendaciones sean coherentes con el contexto de la receta.
    
    Args:
        recommendations: Diccionario con recomendaciones
        recipe_context: Contexto de la receta con restricciones
        
    Returns:
        Tupla de (coherente, problemas)
    """
    coherent = True
    issues = []
    
    # Verificar restricciones dietéticas
    if "sin_gluten" in recipe_context.get("dietary_restrictions", []):
        # Buscar términos prohibidos en recomendaciones
        gluten_terms = ["trigo", "harina", "gluten", "semolina", "espelta", "centeno", "cebada", "triticale", "pan rallado"]
        for rec in recommendations["recommendations"]:
            for term in gluten_terms:
                if term in rec.lower() and "sin gluten" not in rec.lower():
                    coherent = False
                    issues.append(f"Término '{term}' encontrado en recomendación para receta sin gluten")
        
        # Verificar que hay sustituciones para ingredientes con gluten
        has_gluten_subs = False
        for sub in recommendations["substitutions"]:
            if sub.get("restriction") == "sin_gluten":
                has_gluten_subs = True
                break
        
        if not has_gluten_subs and any(term in str(recipe_context).lower() for term in gluten_terms):
            coherent = False
            issues.append("Faltan sustituciones para ingredientes con gluten")
    
    # Verificar coherencia sobre hornos
    if "coccion_inadecuada" in recommendations["issue"]:
        oven_type = recipe_context.get("oven_type", "horno_convencional")
        oven_mentioned = False
        
        for rec in recommendations["recommendations"]:
            if oven_type in rec.lower() or any(ov in rec.lower() for ov in OVEN_RECOMMENDATIONS.keys()):
                oven_mentioned = True
                break
        
        if not oven_mentioned:
            coherent = False
            issues.append(f"No hay recomendaciones específicas para el tipo de horno: {oven_type}")
    
    # Verificar coherencia sobre levadura
    if recipe_context.get("has_yeast", True) == False:
        for rec in recommendations["recommendations"]:
            if "levadura" in rec.lower() and "sin levadura" not in rec.lower():
                coherent = False
                issues.append("Recomendación menciona levadura para receta sin levadura")
    
    return coherent, issues


if __name__ == "__main__":
    # Ejemplo de uso
    cache = RecommendationCache()
    
    # Ejemplo sin gluten con problema de densidad
    sin_gluten_rec = get_contextual_recommendation(
        issue="densidad_alta",
        recipe_type="pizza",
        has_gluten=False,
        has_yeast=True,
        dietary_restrictions=["sin_gluten"],
        oven_type="horno_conveccion",
        cache=cache
    )
    
    print(json.dumps(sin_gluten_rec, indent=2, ensure_ascii=False))
    
    # Verificar coherencia
    recipe_context = {
        "dietary_restrictions": ["sin_gluten"],
        "has_yeast": True,
        "oven_type": "horno_conveccion"
    }
    
    coherent, issues = verify_recommendation_coherence(sin_gluten_rec, recipe_context)
    print(f"\nCoherencia: {coherent}")
    for issue in issues:
        print(f"- {issue}") 