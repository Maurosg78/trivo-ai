#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Módulo de recetas especializadas para masas de alta complejidad.

Este módulo define recetas base para tipos especiales de masa que requieren
técnicas avanzadas o ingredientes específicos, como parte de la expansión
de la biblioteca de recetas del Sprint 4.
"""

from typing import Dict, Any

# Diccionario de recetas especializadas organizadas por categoría
SPECIALTY_DOUGHS = {
    "brioche": {
        "basico": {
            "harina": 100.0,
            "agua": 15.0,
            "leche": 20.0,
            "levadura": 2.0,
            "sal": 2.0,
            "azucar": 10.0,
            "mantequilla": 30.0,  # Alta proporción de mantequilla para textura rica
            "huevo": 25.0,        # Huevos para enriquecer y dar color
            "descripcion": "masa enriquecida de origen francés con alto contenido de mantequilla y huevo, ideal para panes dulces y postres"
        },
        "vegano": {
            "harina": 100.0,
            "agua": 30.0,
            "leche_vegetal": 20.0,
            "levadura": 2.5,
            "sal": 2.0,
            "azucar": 10.0,
            "margarina_vegetal": 25.0,  # Sustituto vegano de la mantequilla
            "pure_manzana": 15.0,       # Sustituto del huevo
            "descripcion": "versión vegana del brioche tradicional que mantiene la suavidad y dulzura característica"
        },
        "integral": {
            "harina": 70.0,
            "harina_integral": 30.0,
            "agua": 20.0,
            "leche": 15.0,
            "levadura": 2.5,
            "sal": 2.0,
            "azucar": 8.0,
            "mantequilla": 25.0,
            "huevo": 20.0,
            "miel": 5.0,
            "descripcion": "brioche con harina integral que aporta mayor valor nutricional manteniendo la textura suave"
        }
    },
    
    "croissant": {
        "clasico": {
            "harina_fuerza": 100.0,  # Harina de alta proteína para mejor laminado
            "agua": 50.0,
            "leche": 5.0,
            "levadura": 2.0,
            "sal": 2.0,
            "azucar": 10.0,
            "mantequilla_laminado": 40.0,  # Mantequilla para laminado
            "huevo_pintar": 5.0,           # Para pintar la superficie
            "descripcion": "auténtico croissant francés con capas de masa y mantequilla laminada para una textura hojaldrada"
        },
        "integral": {
            "harina_fuerza": 75.0,
            "harina_integral": 25.0,
            "agua": 55.0,
            "leche": 5.0,
            "levadura": 2.5,
            "sal": 2.0,
            "azucar": 8.0,
            "mantequilla_laminado": 35.0,
            "huevo_pintar": 5.0,
            "descripcion": "croissant con harina integral que aporta sabor de grano completo manteniendo su estructura hojaldrada"
        },
        "chocolate": {
            "harina_fuerza": 100.0,
            "agua": 50.0,
            "leche": 5.0,
            "levadura": 2.0,
            "sal": 2.0,
            "azucar": 12.0,
            "mantequilla_laminado": 40.0,
            "chocolate_relleno": 15.0,  # Chocolate para rellenar
            "huevo_pintar": 5.0,
            "descripcion": "croissant relleno de chocolate, conocido también como 'pain au chocolat' o 'chocolatine'"
        }
    },
    
    "masa_filo": {
        "tradicional": {
            "harina": 100.0,
            "agua": 45.0,
            "sal": 0.5,
            "aceite_oliva": 5.0,
            "vinagre": 1.0,        # Ayuda a desarrollar el gluten
            "descripcion": "masa extremadamente fina utilizada en la cocina mediterránea y del Medio Oriente para pasteles salados y dulces"
        },
        "rapida": {
            "harina": 100.0,
            "agua": 48.0,
            "sal": 0.5,
            "aceite_oliva": 7.0,
            "vinagre": 1.5,
            "polvo_hornear": 1.0,  # Para una textura más ligera
            "descripcion": "versión más fácil de trabajar de la masa filo, con resultados similares en menos tiempo"
        }
    },
    
    "pasta_fresca": {
        "basica": {
            "harina": 100.0,
            "semola_trigo_duro": 0.0,
            "huevo": 55.0,          # Pasta al huevo tradicional italiana
            "sal": 1.0,
            "aceite_oliva": 2.0,
            "descripcion": "pasta fresca clásica italiana con huevo, ideal para todo tipo de formatos"
        },
        "semola": {
            "harina": 50.0,
            "semola_trigo_duro": 50.0,  # Sémola para textura más firme
            "huevo": 55.0,
            "sal": 1.0,
            "aceite_oliva": 2.0,
            "descripcion": "pasta con sémola de trigo duro que proporciona mejor textura al dente y mayor absorción de salsas"
        },
        "vegana": {
            "harina": 100.0,
            "agua": 35.0,
            "sal": 1.0,
            "aceite_oliva": 5.0,
            "curcuma": 0.5,         # Para dar color amarillo sin huevo
            "descripcion": "pasta sin huevo apropiada para dietas veganas, con curcuma para dar el característico color amarillo"
        },
        "espinaca": {
            "harina": 100.0,
            "huevo": 45.0,
            "pure_espinaca": 20.0,  # Puré de espinacas para color y sabor
            "sal": 1.0,
            "aceite_oliva": 2.0,
            "descripcion": "pasta verde con espinacas, tradicional de algunas regiones italianas"
        },
        "integral": {
            "harina_integral": 100.0,
            "huevo": 60.0,          # Más huevo para compensar la absorción de la harina integral
            "sal": 1.0,
            "aceite_oliva": 3.0,
            "descripcion": "pasta integral con mayor aporte de fibra y nutrientes"
        }
    },
    
    "masa_strudel": {
        "tradicional": {
            "harina": 100.0,
            "agua": 50.0,
            "sal": 0.5,
            "aceite": 3.0,
            "huevo": 10.0,
            "vinagre": 1.0,
            "descripcion": "masa fina de origen austriaco utilizada para el tradicional strudel de manzana y otras versiones dulces o saladas"
        }
    },
    
    "kouign_amann": {
        "tradicional": {
            "harina": 100.0,
            "agua": 60.0,
            "levadura": 2.0,
            "sal": 1.5,
            "azucar_masa": 5.0,
            "mantequilla_laminado": 40.0,
            "azucar_laminado": 30.0,  # Azúcar para laminar con la mantequilla
            "descripcion": "especialidad bretona con capas de masa, mantequilla y azúcar que carameliza durante el horneado"
        }
    }
}

def get_specialty_dough(dough_type: str, variant: str = "basico") -> Dict[str, Any]:
    """
    Obtiene una receta de masa especializada según tipo y variante.
    
    Args:
        dough_type: Tipo de masa especializada (brioche, croissant, etc.)
        variant: Variante específica dentro del tipo (basico, vegano, etc.)
        
    Returns:
        Diccionario con ingredientes y descripción de la receta, o None si no existe
    """
    if dough_type not in SPECIALTY_DOUGHS:
        return None
        
    if variant not in SPECIALTY_DOUGHS[dough_type]:
        # Si la variante específica no existe, intentar con la receta básica
        variant = next(iter(SPECIALTY_DOUGHS[dough_type].keys()))
        
    return SPECIALTY_DOUGHS[dough_type][variant].copy()

def get_all_specialty_types() -> list:
    """
    Devuelve una lista de todos los tipos de masas especiales disponibles.
    
    Returns:
        Lista de strings con los tipos de masas especiales
    """
    return list(SPECIALTY_DOUGHS.keys())

def get_variants_for_type(dough_type: str) -> list:
    """
    Devuelve las variantes disponibles para un tipo de masa.
    
    Args:
        dough_type: Tipo de masa especializada
        
    Returns:
        Lista de strings con las variantes disponibles, o lista vacía si el tipo no existe
    """
    if dough_type not in SPECIALTY_DOUGHS:
        return []
        
    return list(SPECIALTY_DOUGHS[dough_type].keys()) 