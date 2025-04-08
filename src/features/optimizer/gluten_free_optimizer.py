"""
Optimizador genético específico para recetas sin gluten.

Este módulo implementa un optimizador que utiliza algoritmos genéticos para determinar
las mejores proporciones de harinas alternativas sin gluten según el tipo de producto
y las propiedades deseadas.
"""

import random
import copy
from typing import Dict, List, Tuple, Any, Set

class GlutenFreeOptimizer:
    """
    Optimizador específico para recetas sin gluten utilizando algoritmos genéticos.
    Determina dinámicamente las mejores proporciones de harinas alternativas según
    el tipo de producto y las propiedades deseadas.
    """
    
    def __init__(self, population_size=40, generations=25, 
               mutation_rate=0.25, crossover_rate=0.75, elitism_count=3):
        """
        Inicializa el optimizador genético para recetas sin gluten.
        
        Args:
            population_size: Tamaño de la población
            generations: Número de generaciones
            mutation_rate: Tasa de mutación (0-1)
            crossover_rate: Tasa de cruce (0-1)
            elitism_count: Número de mejores individuos que pasan directamente a la siguiente generación
        """
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elitism_count = elitism_count
        
        # Harinas sin gluten disponibles y sus propiedades
        self.gluten_free_flours = {
            "harina_de_arroz": {
                "elasticidad": 0.4,
                "crujiente": 0.7,
                "suavidad": 0.4,
                "ligereza": 0.6,
                "sabor": 0.8,     # Neutral, bueno para muchos usos
                "costo": 0.8      # Relativamente accesible
            },
            "almidon_de_maiz": {
                "elasticidad": 0.2,
                "crujiente": 0.9,
                "suavidad": 0.3,
                "ligereza": 0.7,
                "sabor": 0.9,     # Muy neutral
                "costo": 0.5      # Bajo costo
            },
            "harina_de_almendra": {
                "elasticidad": 0.3,
                "crujiente": 0.4,
                "suavidad": 0.8,
                "ligereza": 0.3,
                "sabor": 0.7,     # Sabor distintivo
                "costo": 0.3      # Costo alto
            },
            "fecula_de_patata": {
                "elasticidad": 0.5,
                "crujiente": 0.6,
                "suavidad": 0.7,
                "ligereza": 0.5,
                "sabor": 0.8,
                "costo": 0.7
            },
            "harina_de_garbanzo": {
                "elasticidad": 0.6,
                "crujiente": 0.4,
                "suavidad": 0.4,
                "ligereza": 0.4,
                "sabor": 0.5,     # Sabor más fuerte
                "costo": 0.9      # Bastante económica
            },
            "harina_de_trigo_sarraceno": {
                "elasticidad": 0.7,
                "crujiente": 0.5,
                "suavidad": 0.5,
                "ligereza": 0.6,
                "sabor": 0.5,
                "costo": 0.6
            },
            "harina_de_mijo": {
                "elasticidad": 0.4,
                "crujiente": 0.7,
                "suavidad": 0.6,
                "ligereza": 0.7,
                "sabor": 0.7,
                "costo": 0.7
            },
            "harina_de_quinoa": {
                "elasticidad": 0.6,
                "crujiente": 0.6,
                "suavidad": 0.5,
                "ligereza": 0.8,
                "sabor": 0.6,
                "costo": 0.4      # Más costosa
            },
            "harina_de_amaranto": {
                "elasticidad": 0.5,
                "crujiente": 0.5,
                "suavidad": 0.5,
                "ligereza": 0.7,
                "sabor": 0.6,
                "costo": 0.4
            },
            "harina_de_tapioca": {
                "elasticidad": 0.7,
                "crujiente": 0.5,
                "suavidad": 0.8,
                "ligereza": 0.5,
                "sabor": 0.8,
                "costo": 0.7
            }
        }
        
        # Aditivos para mejorar textura
        self.texture_additives = {
            "goma_xantana": {
                "elasticidad": 0.9,
                "crujiente": 0.3,
                "suavidad": 0.7,
                "ligereza": 0.6,
                "max_percentage": 0.03,  # Máximo 3% del total de harina
                "min_percentage": 0.01   # Mínimo 1% del total de harina
            },
            "psyllium_husk": {
                "elasticidad": 0.8,
                "crujiente": 0.2,
                "suavidad": 0.8,
                "ligereza": 0.8,
                "max_percentage": 0.05,
                "min_percentage": 0.02
            },
            "goma_guar": {
                "elasticidad": 0.7,
                "crujiente": 0.3,
                "suavidad": 0.8,
                "ligereza": 0.7,
                "max_percentage": 0.03,
                "min_percentage": 0.01
            }
        }
        
        # Perfiles por tipo de producto
        self.product_profiles = {
            "pizza": {
                "elasticidad": 0.8,
                "crujiente": 0.7,
                "suavidad": 0.5,
                "ligereza": 0.6
            },
            "pan": {
                "elasticidad": 0.7,
                "crujiente": 0.5,
                "suavidad": 0.8,
                "ligereza": 0.7
            },
            "galletas": {
                "elasticidad": 0.3,
                "crujiente": 0.9,
                "suavidad": 0.4,
                "ligereza": 0.5
            },
            "pasta": {
                "elasticidad": 0.9,
                "crujiente": 0.3,
                "suavidad": 0.6,
                "ligereza": 0.5
            },
            "tortitas": {
                "elasticidad": 0.5,
                "crujiente": 0.4,
                "suavidad": 0.7,
                "ligereza": 0.8
            }
        }
    
    def optimize(self, product_type: str, desired_properties: Dict[str, bool] = None, 
               cost_weight: float = 0.3) -> Dict[str, Any]:
        """
        Optimiza una receta sin gluten utilizando algoritmos genéticos.
        
        Args:
            product_type: Tipo de producto (pizza, pan, galletas, pasta, tortitas)
            desired_properties: Propiedades específicas deseadas (opcional)
            cost_weight: Importancia del costo en la optimización (0-1)
            
        Returns:
            Diccionario con la receta optimizada y recomendaciones
        """
        # Determinar perfil objetivo
        target_profile = self._get_target_profile(product_type, desired_properties)
        
        # Inicializar población
        population = self._initialize_population()
        
        # Evolución
        for generation in range(self.generations):
            # Evaluar fitness
            fitness_scores = [self._calculate_fitness(individual, target_profile, cost_weight) 
                            for individual in population]
            
            # Ordenar por fitness (mayor es mejor)
            sorted_population = [x for _, x in sorted(zip(fitness_scores, population), 
                                                    key=lambda pair: pair[0], reverse=True)]
            
            if generation == self.generations - 1:
                # Última generación, quedarse con el mejor individuo
                best_recipe = sorted_population[0]
                break
            
            # Seleccionar elites
            new_population = sorted_population[:self.elitism_count]
            
            # Crear el resto de la población
            while len(new_population) < self.population_size:
                # Selección de padres
                parent1 = self._selection(sorted_population, fitness_scores)
                parent2 = self._selection(sorted_population, fitness_scores)
                
                # Cruce
                if random.random() < self.crossover_rate:
                    child1, child2 = self._crossover(parent1, parent2)
                else:
                    child1, child2 = parent1.copy(), parent2.copy()
                
                # Mutación
                if random.random() < self.mutation_rate:
                    child1 = self._mutate(child1)
                if random.random() < self.mutation_rate:
                    child2 = self._mutate(child2)
                
                # Normalizar
                child1 = self._normalize_recipe(child1)
                child2 = self._normalize_recipe(child2)
                
                # Añadir a la nueva población
                new_population.append(child1)
                if len(new_population) < self.population_size:
                    new_population.append(child2)
            
            # Reemplazar población
            population = new_population
        
        # Generar receta final y recomendaciones
        recipe = self._format_recipe(best_recipe, product_type, target_profile)
        
        return recipe
    
    def _get_target_profile(self, product_type: str, desired_properties: Dict[str, bool] = None) -> Dict[str, float]:
        """
        Determina el perfil objetivo basado en el tipo de producto y propiedades deseadas.
        
        Args:
            product_type: Tipo de producto
            desired_properties: Propiedades específicas deseadas
            
        Returns:
            Perfil objetivo con pesos para cada propiedad
        """
        # Establecer perfil base según el tipo de producto
        if product_type in self.product_profiles:
            profile = self.product_profiles[product_type].copy()
        else:
            # Perfil por defecto (pizza)
            profile = self.product_profiles["pizza"].copy()
        
        # Ajustar según propiedades deseadas
        if desired_properties:
            # Incrementar importancia de propiedades específicas
            if desired_properties.get("elasticidad"):
                profile["elasticidad"] = min(1.0, profile["elasticidad"] * 1.3)
            if desired_properties.get("crujiente"):
                profile["crujiente"] = min(1.0, profile["crujiente"] * 1.3)
            if desired_properties.get("suave"):
                profile["suavidad"] = min(1.0, profile["suavidad"] * 1.3)
            if desired_properties.get("ligera"):
                profile["ligereza"] = min(1.0, profile["ligereza"] * 1.3)
        
        return profile
    
    def _initialize_population(self) -> List[Dict[str, float]]:
        """
        Crea una población inicial aleatoria.
        
        Returns:
            Lista de recetas iniciales
        """
        population = []
        
        for _ in range(self.population_size):
            # Crear una receta aleatoria
            recipe = {}
            
            # Seleccionar 3-5 harinas aleatorias
            num_flours = random.randint(3, min(5, len(self.gluten_free_flours)))
            selected_flours = random.sample(list(self.gluten_free_flours.keys()), num_flours)
            
            # Asignar proporciones aleatorias a las harinas
            for flour in selected_flours:
                recipe[flour] = random.random()
            
            # Añadir al menos un aditivo de textura
            selected_additives = random.sample(list(self.texture_additives.keys()), 
                                             random.randint(1, len(self.texture_additives)))
            
            for additive in selected_additives:
                min_val = self.texture_additives[additive]["min_percentage"]
                max_val = self.texture_additives[additive]["max_percentage"]
                recipe[additive] = random.uniform(min_val, max_val)
            
            # Normalizar para que las harinas sumen 1 (excluyendo aditivos)
            recipe = self._normalize_recipe(recipe)
            
            population.append(recipe)
        
        return population
    
    def _calculate_fitness(self, recipe: Dict[str, float], target_profile: Dict[str, float], 
                         cost_weight: float) -> float:
        """
        Calcula la aptitud de una receta según el perfil objetivo.
        
        Args:
            recipe: Receta a evaluar
            target_profile: Perfil objetivo
            cost_weight: Peso del costo en la evaluación
            
        Returns:
            Puntuación de aptitud (mayor es mejor)
        """
        # Inicializar puntuación
        fitness = 100.0
        
        # Calcular propiedades actuales de la receta
        recipe_properties = self._calculate_recipe_properties(recipe)
        
        # Calcular diferencia con el perfil objetivo
        for property_name, target_value in target_profile.items():
            current_value = recipe_properties.get(property_name, 0)
            difference = abs(target_value - current_value)
            
            # Penalizar por diferencia (mayor diferencia = menor aptitud)
            fitness -= difference * 50.0
        
        # Evaluar costo
        recipe_cost = self._calculate_recipe_cost(recipe)
        fitness -= recipe_cost * 20.0 * cost_weight
        
        # Penalizar por ausencia de aditivos importantes
        if not any(additive in recipe for additive in self.texture_additives.keys()):
            fitness -= 30.0
        
        # Penalizar por usar demasiadas harinas diferentes
        flour_count = sum(1 for ingredient in recipe if ingredient in self.gluten_free_flours)
        if flour_count < 2:
            fitness -= 20.0  # Penalizar por usar muy pocas harinas
        elif flour_count > 5:
            fitness -= 10.0 * (flour_count - 5)  # Penalizar por usar demasiadas harinas
        
        return fitness
    
    def _calculate_recipe_properties(self, recipe: Dict[str, float]) -> Dict[str, float]:
        """
        Calcula las propiedades combinadas de una receta.
        
        Args:
            recipe: Receta a evaluar
            
        Returns:
            Propiedades calculadas de la receta
        """
        properties = {
            "elasticidad": 0.0,
            "crujiente": 0.0,
            "suavidad": 0.0,
            "ligereza": 0.0
        }
        
        # Calcular la contribución de harinas
        flour_total = sum(amount for flour, amount in recipe.items() 
                        if flour in self.gluten_free_flours)
        
        if flour_total <= 0:
            return properties
        
        # Normalizar para que las contribuciones sean proporcionales
        for flour, amount in recipe.items():
            if flour in self.gluten_free_flours:
                contribution = amount / flour_total
                for prop in properties:
                    properties[prop] += self.gluten_free_flours[flour][prop] * contribution
            elif flour in self.texture_additives:
                # Los aditivos tienen mayor impacto en proporción
                additive_impact = 5.0  # Factor de impacto
                for prop in properties:
                    if prop in self.texture_additives[flour]:
                        properties[prop] += self.texture_additives[flour][prop] * amount * additive_impact
        
        return properties
    
    def _calculate_recipe_cost(self, recipe: Dict[str, float]) -> float:
        """
        Calcula el costo relativo de una receta.
        
        Args:
            recipe: Receta a evaluar
            
        Returns:
            Costo relativo de la receta (0-1, donde menor es mejor)
        """
        cost = 0.0
        total = 0.0
        
        for ingredient, amount in recipe.items():
            if ingredient in self.gluten_free_flours:
                ingredient_cost = 1.0 - self.gluten_free_flours[ingredient]["costo"]
                cost += ingredient_cost * amount
                total += amount
        
        if total <= 0:
            return 1.0  # Costo máximo si no hay ingredientes válidos
        
        return cost / total
    
    def _selection(self, population: List[Dict[str, float]], fitness_scores: List[float]) -> Dict[str, float]:
        """
        Selecciona un individuo mediante selección por torneo.
        
        Args:
            population: Población actual
            fitness_scores: Puntuaciones de aptitud
            
        Returns:
            Individuo seleccionado
        """
        # Selección por torneo
        tournament_size = 3
        tournament_indices = random.sample(range(len(population)), tournament_size)
        tournament_fitnesses = [fitness_scores[i] for i in tournament_indices]
        
        best_idx = tournament_indices[tournament_fitnesses.index(max(tournament_fitnesses))]
        return population[best_idx].copy()
    
    def _crossover(self, parent1: Dict[str, float], parent2: Dict[str, float]) -> Tuple[Dict[str, float], Dict[str, float]]:
        """
        Realiza cruce entre dos recetas.
        
        Args:
            parent1: Primera receta padre
            parent2: Segunda receta padre
            
        Returns:
            Tupla con dos recetas hijas
        """
        # Unir todos los ingredientes de ambos padres
        all_ingredients = set(parent1.keys()) | set(parent2.keys())
        
        child1 = {}
        child2 = {}
        
        # Cruce aritmético para cada ingrediente
        for ingredient in all_ingredients:
            # Si ambos padres tienen el ingrediente, hacer una mezcla ponderada
            if ingredient in parent1 and ingredient in parent2:
                # Generar valores alpha diferentes para cada hijo
                alpha1 = random.random()
                alpha2 = random.random()
                
                child1[ingredient] = parent1[ingredient] * alpha1 + parent2[ingredient] * (1 - alpha1)
                child2[ingredient] = parent1[ingredient] * (1 - alpha2) + parent2[ingredient] * alpha2
            
            # Si solo un padre tiene el ingrediente, hay 50% de probabilidad de que pase a cada hijo
            elif ingredient in parent1:
                if random.random() < 0.5:
                    child1[ingredient] = parent1[ingredient]
                if random.random() < 0.5:
                    child2[ingredient] = parent1[ingredient]
            elif ingredient in parent2:
                if random.random() < 0.5:
                    child1[ingredient] = parent2[ingredient]
                if random.random() < 0.5:
                    child2[ingredient] = parent2[ingredient]
        
        return child1, child2
    
    def _mutate(self, recipe: Dict[str, float]) -> Dict[str, float]:
        """
        Aplica mutación a una receta.
        
        Args:
            recipe: Receta a mutar
            
        Returns:
            Receta mutada
        """
        mutated = recipe.copy()
        
        # 1. Modificar valores existentes
        for ingredient in list(mutated.keys()):
            if random.random() < 0.3:  # 30% de probabilidad de mutar cada ingrediente
                if ingredient in self.texture_additives:
                    # Para aditivos, mantener en rangos válidos
                    min_val = self.texture_additives[ingredient]["min_percentage"]
                    max_val = self.texture_additives[ingredient]["max_percentage"]
                    mutated[ingredient] = random.uniform(min_val, max_val)
                else:
                    # Para harinas, modificar por un factor aleatorio
                    factor = random.uniform(0.7, 1.3)
                    mutated[ingredient] = mutated[ingredient] * factor
        
        # 2. Agregar un nuevo ingrediente (15% de probabilidad)
        if random.random() < 0.15:
            # Decidir si agregar una harina o un aditivo
            if random.random() < 0.7:  # 70% harina, 30% aditivo
                all_flours = set(self.gluten_free_flours.keys())
                available_flours = all_flours - set(mutated.keys())
                
                if available_flours:
                    new_flour = random.choice(list(available_flours))
                    mutated[new_flour] = random.random() * 0.3  # Cantidad inicial pequeña
            else:
                all_additives = set(self.texture_additives.keys())
                available_additives = all_additives - set(mutated.keys())
                
                if available_additives:
                    new_additive = random.choice(list(available_additives))
                    min_val = self.texture_additives[new_additive]["min_percentage"]
                    max_val = self.texture_additives[new_additive]["max_percentage"]
                    mutated[new_additive] = random.uniform(min_val, max_val)
        
        # 3. Eliminar un ingrediente (10% de probabilidad)
        if random.random() < 0.1:
            # No eliminar aditivos esenciales
            removable = [ing for ing in mutated if ing not in ["goma_xantana"]]
            
            # No eliminar demasiadas harinas
            flour_count = sum(1 for ing in mutated if ing in self.gluten_free_flours)
            if flour_count > 2 and removable:
                to_remove = random.choice(removable)
                mutated.pop(to_remove, None)
        
        return mutated
    
    def _normalize_recipe(self, recipe: Dict[str, float]) -> Dict[str, float]:
        """
        Normaliza las cantidades de la receta.
        
        Args:
            recipe: Receta a normalizar
            
        Returns:
            Receta normalizada
        """
        normalized = recipe.copy()
        
        # Separar harinas y aditivos
        flours = {f: normalized[f] for f in normalized if f in self.gluten_free_flours}
        additives = {a: normalized[a] for a in normalized if a in self.texture_additives}
        
        # Normalizar harinas para que sumen 1
        flour_total = sum(flours.values())
        if flour_total > 0:
            for flour in flours:
                normalized[flour] = flours[flour] / flour_total
        
        # Mantener aditivos dentro de sus rangos
        for additive, amount in additives.items():
            min_val = self.texture_additives[additive]["min_percentage"]
            max_val = self.texture_additives[additive]["max_percentage"]
            normalized[additive] = min(max(amount, min_val), max_val)
        
        return normalized
    
    def _format_recipe(self, recipe: Dict[str, float], product_type: str, 
                     target_profile: Dict[str, float]) -> Dict[str, Any]:
        """
        Formatea la receta final con cantidades reales e instrucciones.
        
        Args:
            recipe: Receta optimizada
            product_type: Tipo de producto
            target_profile: Perfil objetivo usado
            
        Returns:
            Receta formateada con ingredientes, cantidades, instrucciones y recomendaciones
        """
        # Cantidad base de harina (en gramos)
        base_flour_amount = 1000
        
        formatted_ingredients = {}
        
        # Convertir proporciones a cantidades reales
        for ingredient, proportion in recipe.items():
            if ingredient in self.gluten_free_flours:
                formatted_ingredients[ingredient] = round(proportion * base_flour_amount)
            else:
                # Para aditivos, calcular basado en la cantidad total de harina
                formatted_ingredients[ingredient] = round(proportion * base_flour_amount)
        
        # Ingredientes básicos adicionales
        formatted_ingredients["agua"] = round(base_flour_amount * 0.65)  # 65% hidratación base
        formatted_ingredients["sal"] = round(base_flour_amount * 0.02)   # 2% de sal
        formatted_ingredients["aceite_de_oliva"] = round(base_flour_amount * 0.04)  # 4% de aceite
        formatted_ingredients["levadura"] = round(base_flour_amount * 0.01)  # 1% de levadura
        
        # Ajustar agua según tipo de producto
        if product_type == "pizza":
            formatted_ingredients["agua"] = round(base_flour_amount * 0.6)  # 60% para pizza
        elif product_type == "pan":
            formatted_ingredients["agua"] = round(base_flour_amount * 0.7)  # 70% para pan
        elif product_type == "galletas":
            formatted_ingredients["agua"] = round(base_flour_amount * 0.4)  # 40% para galletas
            formatted_ingredients["azucar"] = round(base_flour_amount * 0.15)  # 15% de azúcar
        
        # Generar recomendaciones
        recommendations = self._generate_recommendations(recipe, product_type, target_profile)
        
        # Generar instrucciones específicas
        instructions = self._generate_instructions(product_type)
        
        return {
            "ingredients": formatted_ingredients,
            "recommendations": recommendations,
            "instructions": instructions,
            "properties": self._calculate_recipe_properties(recipe)
        }
    
    def _generate_recommendations(self, recipe: Dict[str, float], product_type: str, 
                               target_profile: Dict[str, float]) -> List[str]:
        """
        Genera recomendaciones para la receta.
        
        Args:
            recipe: Receta optimizada
            product_type: Tipo de producto
            target_profile: Perfil objetivo
            
        Returns:
            Lista de recomendaciones
        """
        recommendations = []
        
        # Recomendaciones generales
        recommendations.append(f"Esta mezcla sin gluten está optimizada para {product_type}.")
        
        # Recomendación sobre hidratación
        if product_type == "pizza":
            recommendations.append("Para masas de pizza sin gluten, mantén el nivel de hidratación alrededor del 60-65%.")
        elif product_type == "pan":
            recommendations.append("Para pan sin gluten, una hidratación del 70-75% dará mejores resultados.")
        elif product_type == "galletas":
            recommendations.append("Para galletas sin gluten, usa menos agua, aproximadamente 40-45% de hidratación.")
        
        # Recomendación sobre combinación de harinas
        if len([f for f in recipe if f in self.gluten_free_flours]) >= 3:
            recommendations.append("La combinación de diferentes harinas sin gluten mejora la textura y el sabor del producto final.")
        
        # Recomendación sobre aditivos
        if "goma_xantana" in recipe:
            recommendations.append("La goma xantana proporciona elasticidad a la masa, similar al gluten.")
        
        if "psyllium_husk" in recipe:
            recommendations.append("El psyllium husk mejora la estructura y retención de humedad en masas sin gluten.")
        
        # Recomendar sobre temperaturas de horneado
        if product_type == "pizza":
            recommendations.append("Hornea a alta temperatura (250-280°C) durante menos tiempo que una pizza tradicional.")
        elif product_type == "pan":
            recommendations.append("Hornea a 220°C durante 10 minutos, luego baja a 190°C hasta que termine de cocerse.")
        
        # Recomendaciones sobre propiedades específicas
        properties = self._calculate_recipe_properties(recipe)
        if properties["elasticidad"] > 0.7:
            recommendations.append("Esta mezcla tiene buena elasticidad, lo que facilita su manipulación.")
        
        if properties["crujiente"] > 0.7:
            recommendations.append("Esta combinación producirá una textura más crujiente.")
        
        if properties["suavidad"] > 0.7:
            recommendations.append("La textura resultante será suave y tierna.")
        
        return recommendations
    
    def _generate_instructions(self, product_type: str) -> List[str]:
        """
        Genera instrucciones para preparar la receta.
        
        Args:
            product_type: Tipo de producto
            
        Returns:
            Lista de instrucciones
        """
        common_instructions = [
            "Mezcla todos los ingredientes secos en un recipiente grande.",
            "Disuelve la levadura en agua tibia (35°C).",
            "Agrega el agua con levadura gradualmente a la mezcla de harinas mientras mezclas.",
            "Añade el aceite de oliva y continúa mezclando hasta formar una masa homogénea.",
            "Las masas sin gluten son más pegajosas que las tradicionales, esto es normal."
        ]
        
        # Instrucciones específicas por tipo de producto
        if product_type == "pizza":
            return common_instructions + [
                "Deja reposar la masa tapada durante 45-60 minutos.",
                "Estira la masa entre dos papeles de hornear usando un rodillo.",
                "Precocina la base 5-7 minutos antes de añadir ingredientes.",
                "Añade los ingredientes y finaliza la cocción durante 8-10 minutos más."
            ]
        elif product_type == "pan":
            return common_instructions + [
                "Amasa vigorosamente durante 5-7 minutos.",
                "Coloca la masa en un molde para pan engrasado.",
                "Deja reposar tapada en un lugar cálido durante 60-90 minutos.",
                "Hornea a 220°C durante 10 minutos, luego baja a 190°C y hornea 30-40 minutos más."
            ]
        elif product_type == "galletas":
            return [
                "Mezcla todos los ingredientes secos en un recipiente.",
                "Añade el aceite o mantequilla fría en trozos pequeños.",
                "Incorpora el agua poco a poco hasta formar una masa que no se pegue.",
                "Enfría la masa en el refrigerador durante 30 minutos.",
                "Estira la masa entre dos papeles hasta obtener el grosor deseado.",
                "Corta las galletas con un cortador.",
                "Hornea a 180°C durante 12-15 minutos hasta que estén ligeramente doradas."
            ]
        else:
            return common_instructions 