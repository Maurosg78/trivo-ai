"""
Módulo de recomendaciones contextuales para TRIVO-AI.

Este módulo proporciona funcionalidades para generar recomendaciones
inteligentes basadas en el contexto de la receta, restricciones dietéticas,
equipo disponible y problemas específicos.
"""

from .knowledge_base import (
    RecommendationCache,
    get_contextual_recommendation,
    verify_recommendation_coherence,
    AERATION_TECHNIQUES,
    GLUTEN_FREE_SOLUTIONS,
    OVEN_RECOMMENDATIONS,
    DIETARY_SUBSTITUTIONS
)

__all__ = [
    'RecommendationCache',
    'get_contextual_recommendation',
    'verify_recommendation_coherence',
    'AERATION_TECHNIQUES',
    'GLUTEN_FREE_SOLUTIONS',
    'OVEN_RECOMMENDATIONS',
    'DIETARY_SUBSTITUTIONS'
] 