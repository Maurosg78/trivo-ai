"""
Middleware para registrar automáticamente las interacciones de ayuda en TRIVO-AI.

Este módulo proporciona decoradores y clases de utilidad para facilitar el registro
automático de las interacciones de ayuda en el sistema, minimizando la necesidad
de código adicional en las funciones que proporcionan ayuda.
"""
import functools
import inspect
import json
import logging
import traceback
from contextlib import contextmanager
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, TypeVar, Union, cast

from src.database.models.help_log import HelpType
from src.services.help_service import HelpService

logger = logging.getLogger(__name__)

# Tipo genérico para la función decorada
F = TypeVar('F', bound=Callable[..., Any])


class HelpContext:
    """
    Contexto para registrar manualmente una interacción de ayuda.
    
    Esta clase permite registrar manualmente una interacción de ayuda
    usando un patrón de contexto (with), facilitando el seguimiento
    de interacciones complejas que involucran múltiples pasos.
    
    Ejemplo de uso:
    ```python
    with HelpContext(user_id="123", help_type=HelpType.RECIPE_CREATION, query="¿Cómo creo una receta?") as ctx:
        # Procesar la consulta...
        result = generate_response(...)
        
        # Registrar la respuesta
        ctx.add_response(result)
        
        # Añadir información adicional de contexto si es necesario
        ctx.update_context({"recipe_template": "basic", "difficulty": "medium"})
        
        # El registro se hará automáticamente al salir del contexto
        return result
    ```
    """
    
    def __init__(
        self,
        user_id: str,
        help_type: Union[HelpType, str],
        query: str,
        recipe_id: Optional[str] = None,
        context_data: Optional[Dict[str, Any]] = None,
    ):
        """
        Inicializa un nuevo contexto de ayuda.
        
        Args:
            user_id: ID del usuario que recibe la ayuda
            help_type: Tipo de ayuda proporcionada
            query: Consulta o pregunta del usuario
            recipe_id: ID de la receta relacionada (opcional)
            context_data: Datos iniciales de contexto (opcional)
        """
        self.user_id = user_id
        self.help_type = help_type
        self.query = query
        self.recipe_id = recipe_id
        self.context_data = context_data or {}
        self.responses: List[str] = []
        self.success = True
        self.error_message = None
        
    def add_response(self, response: str) -> None:
        """
        Añade una respuesta al contexto.
        
        Args:
            response: Texto de la respuesta a registrar
        """
        self.responses.append(response)
    
    def update_context(self, data: Dict[str, Any]) -> None:
        """
        Actualiza los datos de contexto.
        
        Args:
            data: Datos adicionales a incluir en el contexto
        """
        self.context_data.update(data)
    
    def mark_error(self, error_message: str) -> None:
        """
        Marca el contexto como fallido.
        
        Args:
            error_message: Mensaje de error a registrar
        """
        self.success = False
        self.error_message = error_message
    
    def __enter__(self) -> 'HelpContext':
        """Método de entrada para el gestor de contexto."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """
        Método de salida para el gestor de contexto.
        
        Al salir del contexto, se registra automáticamente la interacción de ayuda
        en la base de datos.
        """
        # Si hubo una excepción, marcarla como error
        if exc_type is not None:
            self.success = False
            self.error_message = str(exc_val)
            # Añadir detalles del error al contexto
            self.context_data.update({
                "error_type": exc_type.__name__,
                "error_traceback": traceback.format_exc()
            })
        
        # Combinar todas las respuestas en una sola
        combined_response = "\n".join(self.responses) if self.responses else ""
        
        # Si hubo un error y no hay respuestas, usar el mensaje de error
        if not self.success and not combined_response and self.error_message:
            combined_response = f"ERROR: {self.error_message}"
        
        # Añadir información de éxito/error al contexto
        self.context_data["success"] = self.success
        if self.error_message:
            self.context_data["error_message"] = self.error_message
        
        # Registrar la interacción
        try:
            HelpService.register_help(
                user_id=self.user_id,
                help_type=self.help_type,
                query=self.query,
                response=combined_response,
                context_data=self.context_data,
                recipe_id=self.recipe_id
            )
        except Exception as e:
            logger.error(f"Error al registrar interacción de ayuda: {str(e)}")
        
        # No suprimimos ninguna excepción
        return False


def _reconstruct_query(func: Callable, args: Tuple, kwargs: Dict) -> str:
    """
    Reconstruye la consulta a partir de los argumentos de la función.
    
    Args:
        func: Función decorada
        args: Argumentos posicionales
        kwargs: Argumentos con nombre
        
    Returns:
        Consulta reconstruida o representación de los argumentos
    """
    # Obtener la firma de la función
    sig = inspect.signature(func)
    
    # Buscar argumentos con nombres comunes para consultas
    query_param_names = ["query", "question", "text", "prompt", "input", "message"]
    
    # Mapear argumentos a parámetros
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()
    
    # Buscar el parámetro de consulta
    for name in query_param_names:
        if name in bound_args.arguments:
            value = bound_args.arguments[name]
            if isinstance(value, str):
                return value
    
    # Si no encontramos un parámetro específico, usar el primer argumento string
    for arg in args:
        if isinstance(arg, str):
            return arg
    
    # Como última opción, serializar todos los argumentos
    try:
        # Intentar una representación JSON
        args_repr = {}
        for name, value in bound_args.arguments.items():
            if isinstance(value, (str, int, float, bool, list, dict)) and name != "self":
                args_repr[name] = value
        
        if args_repr:
            return json.dumps(args_repr, ensure_ascii=False)
        
        # Si no hay argumentos serializables, usar el nombre de la función
        return f"Llamada a {func.__name__}"
    except Exception:
        return f"Llamada a {func.__name__} con argumentos no serializables"


def _format_response(result: Any) -> str:
    """
    Formatea el resultado de la función para su registro.
    
    Args:
        result: Resultado de la función decorada
        
    Returns:
        Representación en texto del resultado
    """
    if result is None:
        return "Sin respuesta"
    
    if isinstance(result, str):
        return result
    
    try:
        # Intentar serializar como JSON para objetos estructurados
        if isinstance(result, (dict, list)):
            return json.dumps(result, ensure_ascii=False, default=str)
        
        # Para otros tipos, usar representación de cadena
        return str(result)
    except Exception:
        return f"Resultado no serializable: {type(result).__name__}"


def track_help(
    help_type: Union[HelpType, str],
    user_id_arg: str = "user_id",
    recipe_id_arg: Optional[str] = "recipe_id",
    query_arg: Optional[str] = None
) -> Callable[[F], F]:
    """
    Decorador para registrar automáticamente interacciones de ayuda.
    
    Este decorador captura automáticamente el ID de usuario y, opcionalmente,
    el ID de receta de los argumentos de la función, reconstruye la consulta
    a partir de los argumentos, y registra tanto interacciones exitosas como fallidas.
    
    Args:
        help_type: Tipo de ayuda proporcionada
        user_id_arg: Nombre del argumento que contiene el ID de usuario
        recipe_id_arg: Nombre del argumento que contiene el ID de receta (opcional)
        query_arg: Nombre del argumento que contiene la consulta (opcional)
        
    Returns:
        Decorador configurado
        
    Ejemplo de uso:
    ```python
    @track_help(HelpType.RECIPE_CREATION, user_id_arg="user_id", recipe_id_arg="recipe_id")
    def suggest_recipe_improvements(user_id: str, recipe_id: str, query: str) -> str:
        # La función procesará la consulta normalmente
        # y el decorador registrará automáticamente la interacción
        result = generate_improvement_suggestions(recipe_id, query)
        return result
    ```
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                # Extraer ID de usuario
                user_id = None
                if user_id_arg in kwargs:
                    user_id = kwargs.get(user_id_arg)
                else:
                    # Intentar obtener de los argumentos posicionales
                    sig = inspect.signature(func)
                    param_names = list(sig.parameters.keys())
                    if user_id_arg in param_names:
                        idx = param_names.index(user_id_arg)
                        if idx < len(args):
                            user_id = args[idx]
                
                if not user_id:
                    # Si no podemos obtener el ID de usuario, ejecutar sin registrar
                    logger.warning(f"No se pudo extraer el ID de usuario para {func.__name__}, omitiendo registro")
                    return func(*args, **kwargs)
                
                # Extraer ID de receta si está configurado
                recipe_id = None
                if recipe_id_arg and recipe_id_arg in kwargs:
                    recipe_id = kwargs.get(recipe_id_arg)
                elif recipe_id_arg:
                    # Intentar obtener de los argumentos posicionales
                    sig = inspect.signature(func)
                    param_names = list(sig.parameters.keys())
                    if recipe_id_arg in param_names:
                        idx = param_names.index(recipe_id_arg)
                        if idx < len(args):
                            recipe_id = args[idx]
                
                # Extraer o reconstruir la consulta
                query = None
                if query_arg and query_arg in kwargs:
                    query = kwargs.get(query_arg)
                elif query_arg:
                    # Intentar obtener de los argumentos posicionales
                    sig = inspect.signature(func)
                    param_names = list(sig.parameters.keys())
                    if query_arg in param_names:
                        idx = param_names.index(query_arg)
                        if idx < len(args):
                            query = args[idx]
                
                # Si no se especificó la consulta o no se pudo extraer, reconstruirla
                if not query:
                    query = _reconstruct_query(func, args, kwargs)
                
                # Datos de contexto iniciales
                context_data = {
                    "function": func.__name__,
                    "module": func.__module__
                }
                
                # Ejecutar la función y capturar el resultado
                try:
                    result = func(*args, **kwargs)
                    
                    # Registrar interacción exitosa
                    response = _format_response(result)
                    context_data["success"] = True
                    
                    HelpService.register_help(
                        user_id=user_id,
                        help_type=help_type,
                        query=query,
                        response=response,
                        context_data=context_data,
                        recipe_id=recipe_id
                    )
                    
                    return result
                except Exception as e:
                    # Registrar interacción fallida
                    error_message = str(e)
                    context_data.update({
                        "success": False,
                        "error_type": type(e).__name__,
                        "error_message": error_message,
                        "traceback": traceback.format_exc()
                    })
                    
                    HelpService.register_help(
                        user_id=user_id,
                        help_type=help_type,
                        query=query,
                        response=f"ERROR: {error_message}",
                        context_data=context_data,
                        recipe_id=recipe_id
                    )
                    
                    # Re-lanzar la excepción para mantener el comportamiento original
                    raise
            except Exception as e:
                # Si hay un error en el decorador, registrarlo pero no interrumpir el flujo
                logger.error(f"Error en el decorador track_help para {func.__name__}: {str(e)}")
                # Ejecutar la función original sin más intentos de registro
                return func(*args, **kwargs)
                
        return cast(F, wrapper)
    return decorator 