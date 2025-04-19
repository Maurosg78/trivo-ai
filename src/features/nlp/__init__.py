"""
Módulo de procesamiento de lenguaje natural para TRIVO-AI.

Este módulo contiene funcionalidades para procesar peticiones en lenguaje natural
y convertirlas en recetas con todos los ingredientes y propiedades necesarias.
"""

from .language_processor import LanguageProcessor
from .ai_connector import AIConnector
from .llm_supervisor import LLMSupervisor

__all__ = ['LanguageProcessor', 'AIConnector', 'LLMSupervisor'] 