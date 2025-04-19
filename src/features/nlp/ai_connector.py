"""
Módulo para conectar con servicios de IA externa para procesamiento avanzado
Este componente permite integrar soluciones de IA como Claude, GPT, etc.
para mejorar las capacidades de generación de recetas
"""

import os
import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import time
import random

class AIConnector:
    """
    Conector para servicios de IA externos, permitiendo optimizar recetas
    y generar instrucciones usando modelos avanzados.
    """
    
    def __init__(self, use_supervisor=True):
        """
        Inicializa el conector de IA externa
        
        Args:
            use_supervisor: Si debe utilizarse el LLM supervisor para verificar resultados
        """
        self.logger = logging.getLogger('trivo.ai_connector')
        self.available = self._check_availability()
        
        # Configurar URL base de API
        self.api_url = os.environ.get('EXTERNAL_AI_API_URL', 'https://api.external-ai.example.com')
        
        # Configurar clave API si está disponible
        self.api_key = os.environ.get('EXTERNAL_AI_API_KEY', '')
        
        # Configurar supervisor LLM si está habilitado
        self.use_supervisor = use_supervisor
        self.supervisor = None
        if self.use_supervisor:
            try:
                from .llm_supervisor import LLMSupervisor
                self.supervisor = LLMSupervisor()
                self.logger.info("Supervisor LLM inicializado correctamente")
            except ImportError:
                self.logger.warning("No se pudo cargar el módulo de supervisor LLM")
                self.use_supervisor = False
        
        if self.available:
            self.logger.info("Conector de IA externa inicializado correctamente")
        else:
            self.logger.warning("Conector de IA externa no disponible o deshabilitado")
    
    def _check_availability(self) -> bool:
        """
        Verifica si el conector de IA externa está disponible y configurado
        
        Returns:
            bool: True si está disponible, False en caso contrario
        """
        # Verificar si el servicio está habilitado explícitamente
        if os.environ.get('ENABLE_EXTERNAL_AI', '').lower() == 'false':
            self.logger.info("Servicio de IA externa deshabilitado por configuración")
            return False
        
        # Por ahora, simulamos disponibilidad para desarrollo
        # En producción, esto verificaría conexión real con la API externa
        return True
    
    def optimize_recipe(self, base_ingredients: Dict[str, float], 
                       properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envía los ingredientes base y propiedades a la IA externa para optimizar la receta
        Utiliza el supervisor LLM para verificar y aprobar los resultados si está habilitado
        
        Args:
            base_ingredients: Diccionario de ingredientes base con cantidades
            properties: Propiedades y requisitos de la receta
        
        Returns:
            Diccionario con la receta optimizada, metadatos y resultado de supervisión
        """
        if not self.available:
            raise RuntimeError("El conector de IA externa no está disponible")
            
        try:
            # Preparar payload para la API
            payload = {
                "base_ingredients": base_ingredients,
                "properties": properties,
                "mode": "optimize"
            }
            
            # En un entorno real, esto enviaría una solicitud a la API externa
            # response = self._send_api_request('/recipes/optimize', payload)
            # optimized_recipe = response.json()
            
            # Para desarrollo, simular respuesta de IA
            optimized_recipe = self._simulate_ai_response(base_ingredients, properties)
            
            # Añadir un ID único a la receta
            if "id" not in optimized_recipe:
                optimized_recipe["id"] = f"recipe_{int(time.time())}_{random.randint(1000, 9999)}"
            
            # Añadir propiedades a la receta para referencia
            optimized_recipe["properties"] = properties
            
            # Validar con supervisor LLM si está habilitado
            if self.use_supervisor and self.supervisor:
                self.logger.info(f"Enviando receta al supervisor LLM para revisión: {optimized_recipe['id']}")
                
                # El supervisor revisa la receta
                reviewed_recipe = self.supervisor.review_recipe(optimized_recipe)
                
                # Verificar si la receta fue aprobada o tiene problemas críticos
                if "supervisor_review" in reviewed_recipe:
                    if not reviewed_recipe["supervisor_review"]["approved"]:
                        self.logger.warning(f"Receta {optimized_recipe['id']} rechazada por el supervisor LLM")
                        
                        # Agregar información adicional sobre el rechazo
                        optimized_recipe["supervisor_notes"] = reviewed_recipe["supervisor_review"]["critical_issues"]
                        
                        # Si hay problemas críticos, intentar corregir automáticamente los más comunes
                        if self._should_auto_correct(reviewed_recipe["supervisor_review"]["critical_issues"]):
                            self.logger.info("Intentando corregir automáticamente la receta")
                            corrected_recipe = self._auto_correct_recipe(optimized_recipe, 
                                                                       reviewed_recipe["supervisor_review"])
                            
                            # Volver a revisar la receta corregida
                            re_reviewed_recipe = self.supervisor.review_recipe(corrected_recipe)
                            
                            if re_reviewed_recipe["supervisor_review"]["approved"]:
                                self.logger.info(f"Receta {corrected_recipe['id']} corregida y aprobada")
                                return re_reviewed_recipe
                    else:
                        self.logger.info(f"Receta {optimized_recipe['id']} aprobada por el supervisor LLM")
                        
                        # Agregar sugerencias de mejora si hay
                        if reviewed_recipe["supervisor_review"]["improvement_suggestions"]:
                            optimized_recipe["improvement_suggestions"] = \
                                reviewed_recipe["supervisor_review"]["improvement_suggestions"]
                
                return reviewed_recipe
            
            return optimized_recipe
            
        except Exception as e:
            self.logger.error(f"Error al optimizar receta con IA externa: {str(e)}")
            raise
    
    def generate_instructions(self, recipe_data: Dict[str, Any], 
                             user_request: str) -> List[str]:
        """
        Genera instrucciones detalladas para la receta utilizando IA
        
        Args:
            recipe_data: Datos de la receta optimizada
            user_request: Texto original del usuario
        
        Returns:
            Lista de instrucciones paso a paso
        """
        if not self.available:
            raise RuntimeError("El conector de IA externa no está disponible")
            
        try:
            # Preparar payload para la API
            payload = {
                "recipe": recipe_data,
                "user_request": user_request,
                "mode": "instructions"
            }
            
            # En un entorno real, esto enviaría una solicitud a la API externa
            # response = self._send_api_request('/recipes/instructions', payload)
            # instructions = response.json().get("instructions", [])
            
            # Para desarrollo, simular respuesta de IA
            instructions = self._simulate_instructions(recipe_data, user_request)
            
            # Verificar instrucciones con supervisor LLM si está habilitado
            if self.use_supervisor and self.supervisor:
                # Crear una copia del recipe_data para adjuntar las instrucciones
                recipe_with_instructions = recipe_data.copy()
                recipe_with_instructions["instructions"] = instructions
                
                # El supervisor revisa la receta con instrucciones
                reviewed_data = self.supervisor.review_recipe(recipe_with_instructions)
                
                # Verificar si hay problemas con las instrucciones
                if "supervisor_review" in reviewed_data:
                    review = reviewed_data["supervisor_review"]
                    
                    if not review["approved"]:
                        self.logger.warning("Instrucciones rechazadas por el supervisor LLM")
                        
                        # Intentar corregir las instrucciones según el feedback
                        instruction_issues = [issue for issue in review["critical_issues"] 
                                            if "instruc" in issue.lower()]
                        
                        if instruction_issues and len(instructions) > 0:
                            self.logger.info("Mejorando instrucciones basado en feedback del supervisor")
                            return self._enhance_instructions(instructions, instruction_issues)
                    
                    # Si hay sugerencias de mejora para las instrucciones, aplicarlas
                    instruction_suggestions = [sugg for sugg in review.get("improvement_suggestions", [])
                                            if "instruc" in sugg.lower() or "temp" in sugg.lower() 
                                            or "tiemp" in sugg.lower()]
                    
                    if instruction_suggestions and len(instructions) > 0:
                        self.logger.info("Aplicando sugerencias del supervisor a las instrucciones")
                        return self._enhance_instructions(instructions, instruction_suggestions)
                    
                    # Si no hay problemas específicos con las instrucciones, devolverlas como están
                    return reviewed_data.get("instructions", instructions)
            
            return instructions
            
        except Exception as e:
            self.logger.error(f"Error al generar instrucciones con IA externa: {str(e)}")
            raise
    
    def analyze_lifecycle(self, recipe_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza el ciclo de vida completo de una receta, generando proyecciones
        de producción, costos y viabilidad de mercado.
        
        Args:
            recipe_data: Datos completos de la receta
            
        Returns:
            Diccionario con análisis completo del ciclo de vida
        """
        if not self.available:
            raise RuntimeError("El conector de IA externa no está disponible")
            
        try:
            # En un entorno real, esto enviaría una solicitud a la API externa
            # response = self._send_api_request('/recipes/lifecycle', {"recipe": recipe_data})
            # lifecycle_data = response.json()
            
            # Para desarrollo, simular análisis de ciclo de vida
            lifecycle_data = self._simulate_lifecycle_analysis(recipe_data)
            
            # Validar con supervisor LLM si está habilitado
            if self.use_supervisor and self.supervisor:
                self.logger.info("Enviando análisis de ciclo de vida al supervisor LLM")
                
                # El supervisor revisa el análisis
                reviewed_analysis = self.supervisor.review_lifecycle_analysis(lifecycle_data)
                
                # Verificar si el análisis fue aprobado
                if "supervisor_review" in reviewed_analysis:
                    if not reviewed_analysis["supervisor_review"]["approved"]:
                        self.logger.warning("Análisis de ciclo de vida rechazado por el supervisor LLM")
                    else:
                        self.logger.info("Análisis de ciclo de vida aprobado por el supervisor LLM")
                
                return reviewed_analysis
            
            return lifecycle_data
            
        except Exception as e:
            self.logger.error(f"Error al analizar ciclo de vida: {str(e)}")
            raise
    
    def _send_api_request(self, endpoint: str, data: Dict[str, Any]) -> requests.Response:
        """
        Envía una solicitud a la API externa
        
        Args:
            endpoint: Ruta del endpoint de la API
            data: Datos a enviar en la solicitud
            
        Returns:
            Respuesta de la API
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}" if self.api_key else ""
        }
        
        url = f"{self.api_url}{endpoint}"
        response = requests.post(url, json=data, headers=headers)
        
        # Verificar si la solicitud fue exitosa
        response.raise_for_status()
        
        return response
    
    def _simulate_ai_response(self, base_ingredients: Dict[str, float], 
                            properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simula una respuesta de IA para desarrollo
        
        Args:
            base_ingredients: Ingredientes base
            properties: Propiedades de la receta
            
        Returns:
            Datos de la receta simulada
        """
        # Simular tiempo de procesamiento
        time.sleep(0.5)
        
        # Copiar ingredientes base
        optimized_ingredients = base_ingredients.copy()
        
        # Ajustar cantidades para simular optimización
        for ingredient in optimized_ingredients:
            # Ajuste aleatorio entre -5% y +15%
            adjustment = 1.0 + (random.uniform(-0.05, 0.15))
            optimized_ingredients[ingredient] = round(optimized_ingredients[ingredient] * adjustment, 1)
        
        # Añadir ingredientes adicionales según propiedades
        color = properties.get('color')
        if color == 'red':
            optimized_ingredients['remolacha en polvo'] = 15.0
        elif color == 'green':
            optimized_ingredients['espinaca en polvo'] = 15.0
        
        # Verificar restricciones dietéticas
        restrictions = properties.get('dietary_restrictions', [])
        
        # Ajustes para recetas sin gluten
        if 'gluten-free' in restrictions:
            # Asegurar que no haya ingredientes con gluten
            if 'harina de trigo' in optimized_ingredients:
                del optimized_ingredients['harina de trigo']
                optimized_ingredients['harina de arroz'] = 300.0
                optimized_ingredients['fécula de maíz'] = 100.0
                optimized_ingredients['harina de almendras'] = 100.0
                optimized_ingredients['goma xantana'] = 10.0
        
        # Ajustes para recetas veganas
        if 'vegan' in restrictions and 'huevo' in optimized_ingredients:
            del optimized_ingredients['huevo']
            optimized_ingredients['semillas de lino molidas'] = 25.0
            optimized_ingredients['agua (para lino)'] = 75.0
        
        # Crear respuesta simulada
        response = {
            "ingredients": optimized_ingredients,
            "rationale": "Receta optimizada a través de algoritmos genéticos para maximizar textura y sabor.",
            "key_tip": "Para mejores resultados, deja fermentar la masa en refrigeración por 24 horas."
        }
        
        # Agregar información de adaptaciones según las propiedades
        adaptations = []
        
        if 'gluten-free' in restrictions:
            adaptations.append("Formulación adaptada para eliminar completamente el gluten, manteniendo textura y elasticidad.")
        
        if 'vegan' in restrictions:
            adaptations.append("Formulación 100% vegana con sustitutos funcionales que mantienen las propiedades de la masa.")
        
        if color:
            adaptations.append(f"Color {color} natural logrado con ingredientes vegetales sin aditivos artificiales.")
        
        scale = properties.get('scale', 'medium')
        if scale == 'large':
            adaptations.append("Proporciones ajustadas para tamaño familiar, manteniendo la estructura óptima.")
        elif scale == 'small':
            adaptations.append("Formulación ajustada para tamaño individual, preservando textura y cocción uniforme.")
        
        if adaptations:
            response["adaptations"] = adaptations
        
        return response
    
    def _simulate_instructions(self, recipe_data: Dict[str, Any], 
                             user_request: str) -> List[str]:
        """
        Simula instrucciones detalladas generadas por IA
        
        Args:
            recipe_data: Datos de la receta
            user_request: Solicitud original del usuario
            
        Returns:
            Lista de instrucciones generadas
        """
        # Obtener propiedades relevantes
        ingredients = recipe_data.get('ingredients', {})
        properties = recipe_data.get('properties', {})
        
        dietary_restrictions = properties.get('dietary_restrictions', [])
        is_gluten_free = 'gluten-free' in dietary_restrictions
        is_vegan = 'vegan' in dietary_restrictions
        scale = properties.get('scale', 'medium')
        color = properties.get('color')
        
        # Instrucciones base
        instructions = [
            "Reúne todos los ingredientes y asegúrate de que estén a temperatura ambiente para una mejor integración.",
            "En un recipiente grande, mezcla todos los ingredientes secos incluyendo la harina, sal y levadura seca.",
            "Forma un hueco en el centro y agrega los ingredientes líquidos gradualmente mientras mezclas.",
        ]
        
        # Ajustes para recetas veganas
        if is_vegan and 'semillas de lino molidas' in ingredients:
            instructions.insert(2, "Prepara el sustituto de huevo mezclando las semillas de lino molidas con agua tibia y deja reposar 5 minutos hasta formar un gel.")
        
        # Proceso de amasado según tipo de masa
        if is_gluten_free:
            instructions.append("Mezcla vigorosamente hasta integrar todos los ingredientes. La masa sin gluten será más pegajosa que una tradicional.")
            instructions.append("No es necesario amasar excesivamente una masa sin gluten. Mezcla solo hasta que los ingredientes estén bien integrados, aproximadamente 3-4 minutos.")
        else:
            instructions.append("Amasa sobre una superficie ligeramente enharinada durante 8-10 minutos hasta que la masa esté suave y elástica.")
            instructions.append("Realiza la prueba de la ventana: estira un pedazo pequeño de masa; debe ser lo suficientemente elástica para formar una fina membrana translúcida sin romperse.")
        
        # Instrucciones de fermentación
        if is_gluten_free:
            instructions.append("Coloca la masa en un recipiente ligeramente aceitado, cubre con film transparente y deja reposar en un lugar cálido durante 30-45 minutos. Las masas sin gluten no requieren tanta fermentación como las tradicionales.")
        else:
            instructions.append("Forma una bola con la masa y colócala en un recipiente ligeramente aceitado. Cubre con un paño húmedo o film transparente.")
            instructions.append("Deja que la masa fermente en un lugar cálido durante 1-2 horas, o hasta que duplique su tamaño. Para desarrollar más sabor, puedes refrigerar la masa y dejarla fermentar lentamente durante 24-48 horas.")
        
        # Ajustes según el tamaño de la pizza
        if scale == 'large':
            instructions.append("Divide la masa en 2 porciones iguales para hacer 2 pizzas familiares grandes de aproximadamente 35-40 cm de diámetro.")
        elif scale == 'small':
            instructions.append("Divide la masa en 4 porciones para hacer pizzas individuales de aproximadamente 20 cm de diámetro.")
        else:
            instructions.append("Esta cantidad es perfecta para una pizza mediana de 30 cm o dos pizzas pequeñas de 20 cm de diámetro.")
        
        # Instrucciones de formado y horneado
        instructions.extend([
            "Estira cada porción de masa con un rodillo sobre una superficie ligeramente enharinada hasta obtener el grosor deseado, aproximadamente 5 mm.",
            "Transfiere la masa a una bandeja para hornear previamente enharinada o con papel de hornear.",
            "Agrega una fina capa de salsa de tomate, dejando un borde de aproximadamente 1 cm sin cubrir para formar la corteza.",
            "Añade tus ingredientes favoritos y un toque final de aceite de oliva.",
        ])
        
        # Instrucciones de horneado
        instructions.append("Precalienta el horno a la temperatura máxima (generalmente 250-280°C) durante al menos 30 minutos, idealmente con una piedra o bandeja de hornear dentro.")
        instructions.append("Hornea la pizza en la rejilla inferior del horno durante 8-12 minutos, o hasta que los bordes estén dorados y la base crujiente.")
        
        # Instrucciones especiales según propiedades
        if color:
            instructions.append(f"Notarás que la masa tiene un hermoso color {color} natural gracias a los ingredientes especiales incorporados en la receta.")
        
        if is_gluten_free:
            instructions.append("CONSEJO IMPORTANTE: Las pizzas sin gluten son más frágiles cuando están calientes. Deja enfriar ligeramente antes de cortarla para evitar que se desmorone.")
        
        # Instrucción final
        instructions.append("Saca la pizza del horno, déjala reposar durante 1-2 minutos, córtala en porciones y sirve inmediatamente. ¡Disfruta tu pizza TRIVO-AI personalizada!")
        
        return instructions
    
    def _simulate_lifecycle_analysis(self, recipe_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simula un análisis de ciclo de vida para desarrollo
        
        Args:
            recipe_data: Datos de la receta
            
        Returns:
            Análisis simulado del ciclo de vida
        """
        # Obtener parámetros relevantes
        properties = recipe_data.get('properties', {})
        scale = properties.get('scale', 'medium')
        has_restrictions = 'dietary_restrictions' in properties and len(properties['dietary_restrictions']) > 0
        
        # Calcular duración de etapas según propiedades
        development_days = 42 if has_restrictions else 30
        testing_days = 15 if has_restrictions else 10
        production_setup_days = 20
        
        if scale == 'large':
            production_setup_days += 10
        elif scale == 'small':
            production_setup_days -= 5
        
        # Generar fechas simuladas
        today = datetime.now()
        development_start = today.strftime('%Y-%m-%d')
        
        # Crear análisis de ciclo de vida simulado
        lifecycle_data = {
            "recipe_id": recipe_data.get("id", "unknown"),
            "stages": [
                {
                    "name": "Desarrollo",
                    "status": "completed",
                    "date": development_start,
                    "duration": development_days,
                    "owner": "María López"
                },
                {
                    "name": "Pruebas",
                    "status": "in_progress",
                    "date": development_start,
                    "duration": testing_days,
                    "owner": "Carlos Gómez"
                },
                {
                    "name": "Producción",
                    "status": "pending",
                    "date": None,
                    "duration": production_setup_days,
                    "owner": "Ana Martínez"
                },
                {
                    "name": "Distribución",
                    "status": "pending",
                    "date": None,
                    "duration": 30,
                    "owner": "Pedro Sánchez"
                }
            ],
            "costs": {
                "materias_primas": self._calculate_ingredient_costs(recipe_data.get('ingredients', {})),
                "mano_obra": 350 + (100 if has_restrictions else 0),
                "equipamiento": 500 if scale == 'large' else (300 if scale == 'medium' else 150),
                "costo_total": 0,  # Se calculará más adelante
                "precio_venta": 0  # Se calculará más adelante
            },
            "feasibility": {
                "technical_score": 7 if not has_restrictions else 6,
                "market_score": 8 if has_restrictions else 7,
                "economic_score": 7 if scale != 'small' else 6,
                "recommendation": "proceed"
            }
        }
        
        # Calcular costo total
        total_cost = sum(cost for category, cost in lifecycle_data["costs"].items() 
                         if category not in ["costo_total", "precio_venta"])
        
        # Redondear a la centena más cercana
        total_cost = round(total_cost / 100) * 100
        
        # Calcular precio de venta con margen del 40%
        sale_price = round(total_cost / 0.6)
        
        # Actualizar costos
        lifecycle_data["costs"]["costo_total"] = total_cost
        lifecycle_data["costs"]["precio_venta"] = sale_price
        
        return lifecycle_data
    
    def _calculate_ingredient_costs(self, ingredients: Dict[str, float]) -> float:
        """
        Calcula el costo aproximado de los ingredientes basado en cantidades
        
        Args:
            ingredients: Diccionario de ingredientes con cantidades
            
        Returns:
            Costo total estimado
        """
        # Precios simulados por kilogramo
        prices = {
            "harina": 1.2,
            "agua": 0.01,
            "sal": 0.8,
            "levadura": 15.0,
            "aceite": 5.0,
            "xantana": 50.0,
            "arroz": 2.5,
            "almendra": 12.0,
            "maíz": 1.8,
            "lino": 6.0,
            "espinaca": 8.0,
            "remolacha": 6.0
        }
        
        total_cost = 0
        
        for ingredient, amount in ingredients.items():
            # Buscar el precio aproximado basado en palabras clave
            ingredient_price = None
            for key, price in prices.items():
                if key in ingredient.lower():
                    ingredient_price = price
                    break
            
            # Si no se encuentra, usar un valor predeterminado
            if ingredient_price is None:
                ingredient_price = 3.0
            
            # Convertir gramos a kg y calcular costo
            cost = (amount / 1000) * ingredient_price
            total_cost += cost
        
        # Agregar factor de seguridad del 20%
        return total_cost * 1.2
    
    def _should_auto_correct(self, issues: List[str]) -> bool:
        """
        Determina si los problemas detectados pueden ser corregidos automáticamente
        
        Args:
            issues: Lista de problemas críticos
            
        Returns:
            True si se puede intentar una corrección automática, False en caso contrario
        """
        # Verificar si hay problemas conocidos que se puedan corregir
        correctable_issues = [
            "gluten", "hidratación", "levadura", "agente", "vegana", "huevo", "leche"
        ]
        
        return any(any(item in issue.lower() for item in correctable_issues) for issue in issues)
    
    def _auto_correct_recipe(self, recipe: Dict[str, Any], 
                           review: Dict[str, Any]) -> Dict[str, Any]:
        """
        Intenta corregir automáticamente los problemas más comunes en una receta
        
        Args:
            recipe: Receta original con problemas
            review: Revisión del supervisor con problemas identificados
            
        Returns:
            Receta corregida
        """
        # Crear una copia para no modificar la original
        corrected = recipe.copy()
        ingredients = corrected.get("ingredients", {}).copy()
        properties = corrected.get("properties", {}).copy()
        
        # Recorrer los problemas críticos
        for issue in review.get("critical_issues", []):
            issue_lower = issue.lower()
            
            # Corregir problemas de hidratación
            if "hidratación" in issue_lower:
                if "excesiva" in issue_lower:
                    # Reducir agua
                    for ing, amount in ingredients.items():
                        if "agua" in ing.lower():
                            ingredients[ing] = round(amount * 0.8, 1)  # Reducir 20%
                elif "baja" in issue_lower:
                    # Aumentar agua
                    for ing, amount in ingredients.items():
                        if "agua" in ing.lower():
                            ingredients[ing] = round(amount * 1.2, 1)  # Aumentar 20%
            
            # Corregir problemas de levadura
            elif "levadura" in issue_lower or "fermentativo" in issue_lower:
                # Añadir levadura si falta
                ingredients["levadura seca"] = 7.0
            
            # Corregir problemas de gluten
            elif "gluten" in issue_lower and "sin gluten" in issue_lower:
                # Quitar ingredientes con gluten
                gluten_ingredients = ["harina de trigo", "sémola", "harina de centeno"]
                for gluten_ing in gluten_ingredients:
                    for ing in list(ingredients.keys()):
                        if gluten_ing in ing.lower():
                            del ingredients[ing]
                
                # Añadir ingredientes sin gluten
                ingredients["harina de arroz"] = 300.0
                ingredients["fécula de maíz"] = 100.0
                ingredients["harina de almendras"] = 100.0
                ingredients["goma xantana"] = 10.0
            
            # Corregir problemas veganos
            elif "vegana" in issue_lower:
                non_vegan = ["huevo", "leche", "mantequilla", "miel", "yogur"]
                for non_vegan_ing in non_vegan:
                    for ing in list(ingredients.keys()):
                        if non_vegan_ing in ing.lower():
                            del ingredients[ing]
                            
                            # Reemplazar con alternativas si es necesario
                            if "huevo" in ing.lower():
                                ingredients["semillas de lino molidas"] = 25.0
                                ingredients["agua (para lino)"] = 75.0
                            elif "leche" in ing.lower() or "yogur" in ing.lower():
                                ingredients["leche de almendras"] = 100.0
                            elif "mantequilla" in ing.lower():
                                ingredients["aceite de oliva"] = 50.0
        
        # Actualizar la receta corregida
        corrected["ingredients"] = ingredients
        corrected["properties"] = properties
        
        return corrected
    
    def _enhance_instructions(self, instructions: List[str], 
                            feedback: List[str]) -> List[str]:
        """
        Mejora las instrucciones basándose en el feedback del supervisor
        
        Args:
            instructions: Instrucciones originales
            feedback: Feedback del supervisor
            
        Returns:
            Instrucciones mejoradas
        """
        enhanced = instructions.copy()
        
        # Analizar el feedback y aplicar mejoras
        for item in feedback:
            item_lower = item.lower()
            
            # Añadir temperatura si falta
            if "temperatura" in item_lower:
                has_temp = any("°c" in instruction.lower() or "grados" in instruction.lower() 
                              for instruction in enhanced)
                
                if not has_temp:
                    for i, instruction in enumerate(enhanced):
                        if "horno" in instruction.lower() and "precalienta" in instruction.lower():
                            enhanced[i] = instruction.replace("precalienta el horno", 
                                                           "precalienta el horno a 220°C (430°F)")
                            break
                    else:
                        # Si no se encuentra una instrucción adecuada, añadir una nueva
                        enhanced.append("Asegúrate de precalentar el horno a 220°C (430°F) antes de hornear.")
            
            # Añadir tiempos si faltan
            if "tiempo" in item_lower:
                has_time = any(("minuto" in instruction.lower() or "hora" in instruction.lower()) 
                              for instruction in enhanced)
                
                if not has_time:
                    for i, instruction in enumerate(enhanced):
                        if "ferment" in instruction.lower() and not any(t in instruction.lower() 
                                                                     for t in ["minuto", "hora"]):
                            enhanced[i] = instruction + " Este proceso toma aproximadamente 60-90 minutos."
                            break
            
            # Añadir más instrucciones si son insuficientes
            if "insuficiente" in item_lower and len(enhanced) < 5:
                enhanced.append("Asegúrate de que todos los ingredientes estén a temperatura ambiente antes de comenzar.")
                enhanced.append("Lava bien tus manos antes de manipular la masa.")
                enhanced.append("Para mejores resultados, usa un termómetro de cocina para verificar que el centro de la masa alcance la temperatura adecuada.")
        
        return enhanced 