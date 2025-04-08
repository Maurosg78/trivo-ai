"""
Paquete para la biblioteca de recetas de TRIVO-AI

Este paquete contiene definiciones de distintos tipos de masas,
desde recetas básicas hasta especializadas, organizadas por categorías
y con variantes para diferentes propósitos.
"""

from src.data.recipes_db.specialty_doughs import (
    get_specialty_dough,
    get_all_specialty_types,
    get_variants_for_type,
    SPECIALTY_DOUGHS
)

__all__ = [
    'get_specialty_dough',
    'get_all_specialty_types',
    'get_variants_for_type',
    'SPECIALTY_DOUGHS'
] 