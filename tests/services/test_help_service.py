import json
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy.exc import SQLAlchemyError

from src.database.models.help_log import HelpLog, HelpType
from src.services.help_middleware import HelpContext, track_help
from src.services.help_service import HelpService


class TestHelpService(unittest.TestCase):
    """Pruebas para el servicio de ayuda."""

    @patch("src.services.help_service.db")
    def test_register_help(self, mock_db):
        """Prueba el registro de una nueva interacción de ayuda."""
        # Configuración
        user_id = "user123"
        help_type = HelpType.RECIPE_CREATION
        query = "¿Cómo creo una receta?"
        response = "Aquí te muestro cómo crear una receta..."
        context_data = {"dificultad": "fácil"}
        recipe_id = "recipe456"

        # Ejecución
        result = HelpService.register_help(
            user_id=user_id,
            help_type=help_type,
            query=query,
            response=response,
            context_data=context_data,
            recipe_id=recipe_id
        )

        # Verificación
        mock_db.session.add.assert_called_once()
        mock_db.session.commit.assert_called_once()
        
        # Verificar que se creó el objeto HelpLog correcto
        help_log = mock_db.session.add.call_args[0][0]
        assert isinstance(help_log, HelpLog)
        assert help_log.user_id == user_id
        assert help_log.help_type == help_type
        assert help_log.query == query
        assert help_log.response == response
        assert help_log.context_data == context_data
        assert help_log.recipe_id == recipe_id

    @patch("src.services.help_service.db")
    def test_register_help_with_string_help_type(self, mock_db):
        """Prueba el registro con tipo de ayuda como string."""
        # Configuración
        user_id = "user123"
        help_type = "RECIPE_CREATION"  # String en lugar de enum
        query = "¿Cómo creo una receta?"
        response = "Aquí te muestro cómo crear una receta..."

        # Ejecución
        result = HelpService.register_help(
            user_id=user_id,
            help_type=help_type,
            query=query,
            response=response
        )

        # Verificación
        mock_db.session.add.assert_called_once()
        help_log = mock_db.session.add.call_args[0][0]
        assert help_log.help_type == HelpType.RECIPE_CREATION

    @patch("src.services.help_service.db")
    def test_register_help_with_invalid_help_type(self, mock_db):
        """Prueba el manejo de un tipo de ayuda inválido."""
        # Configuración
        user_id = "user123"
        help_type = "TIPO_INVALIDO"
        query = "¿Cómo creo una receta?"
        response = "Aquí te muestro cómo crear una receta..."

        # Verificación
        with pytest.raises(ValueError):
            HelpService.register_help(
                user_id=user_id,
                help_type=help_type,
                query=query,
                response=response
            )

    @patch("src.services.help_service.db")
    def test_register_help_db_error(self, mock_db):
        """Prueba el manejo de errores de base de datos."""
        # Configuración
        mock_db.session.commit.side_effect = SQLAlchemyError("Error de BD")
        
        # Verificación
        with pytest.raises(SQLAlchemyError):
            HelpService.register_help(
                user_id="user123",
                help_type=HelpType.RECIPE_CREATION,
                query="¿Qué receta puedo hacer?",
                response="Puedes hacer pizza"
            )
        
        # Verificar que se intentó hacer rollback
        mock_db.session.rollback.assert_called_once()

    @patch("src.services.help_service.db")
    def test_get_user_help_history(self, mock_db):
        """Prueba la obtención del historial de ayuda de un usuario."""
        # Configuración
        user_id = "user123"
        mock_help_logs = [
            MagicMock(to_dict=MagicMock(return_value={"id": 1})),
            MagicMock(to_dict=MagicMock(return_value={"id": 2}))
        ]
        
        # Configurar la consulta y su resultado
        mock_query = MagicMock()
        mock_db.session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_help_logs
        
        # Ejecución
        result = HelpService.get_user_help_history(user_id)
        
        # Verificación
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["id"] == 2
        
        # Verificar que se llamó a las funciones correctas
        mock_db.session.query.assert_called_once_with(HelpLog)
        mock_query.filter.assert_called_once()
        mock_query.order_by.assert_called_once()

    @patch("src.services.help_service.db")
    def test_get_recipe_help_history(self, mock_db):
        """Prueba la obtención del historial de ayuda para una receta."""
        # Configuración
        recipe_id = "recipe456"
        mock_help_logs = [
            MagicMock(to_dict=MagicMock(return_value={"id": 3})),
            MagicMock(to_dict=MagicMock(return_value={"id": 4}))
        ]
        
        # Configurar la consulta y su resultado
        mock_query = MagicMock()
        mock_db.session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = mock_help_logs
        
        # Ejecución
        result = HelpService.get_recipe_help_history(recipe_id)
        
        # Verificación
        assert len(result) == 2
        assert result[0]["id"] == 3
        assert result[1]["id"] == 4

    @patch("src.services.help_service.db")
    def test_get_help_statistics(self, mock_db):
        """Prueba la obtención de estadísticas de ayuda."""
        # Configuración
        mock_db.session.query.return_value.count.return_value = 100
        
        # Ejecución
        result = HelpService.get_help_statistics()
        
        # Verificación
        assert result["total_help_interactions"] == 100
        
    @patch("src.services.help_service.db")
    def test_search_help_logs(self, mock_db):
        """Prueba la búsqueda en los registros de ayuda."""
        # Configuración
        mock_help_logs = [
            MagicMock(to_dict=MagicMock(return_value={"id": 5})),
            MagicMock(to_dict=MagicMock(return_value={"id": 6}))
        ]
        
        # Configurar la consulta y su resultado
        mock_query = MagicMock()
        mock_db.session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = mock_help_logs
        
        # Fechas para la búsqueda
        start_date = datetime.now() - timedelta(days=7)
        end_date = datetime.now()
        
        # Ejecución
        result = HelpService.search_help_logs(
            query_text="receta",
            help_type=HelpType.RECIPE_CREATION,
            user_id="user123",
            recipe_id="recipe456",
            start_date=start_date,
            end_date=end_date,
            limit=10,
            offset=0
        )
        
        # Verificación
        assert len(result) == 2
        assert result[0]["id"] == 5
        assert result[1]["id"] == 6
        
        # Verificar que se filtra correctamente
        assert mock_query.filter.call_count >= 5  # Al menos 5 filtros

    @patch("src.services.help_service.db")
    def test_delete_help_log(self, mock_db):
        """Prueba la eliminación de un registro de ayuda."""
        # Configuración
        log_id = 123
        mock_log = MagicMock()
        mock_db.session.query.return_value.filter.return_value.first.return_value = mock_log
        
        # Ejecución
        result = HelpService.delete_help_log(log_id)
        
        # Verificación
        assert result is True
        mock_db.session.delete.assert_called_once_with(mock_log)
        mock_db.session.commit.assert_called_once()

    @patch("src.services.help_service.db")
    def test_delete_help_log_not_found(self, mock_db):
        """Prueba la eliminación de un registro inexistente."""
        # Configuración
        log_id = 999
        mock_db.session.query.return_value.filter.return_value.first.return_value = None
        
        # Ejecución
        result = HelpService.delete_help_log(log_id)
        
        # Verificación
        assert result is False
        mock_db.session.delete.assert_not_called()


class TestHelpMiddleware(unittest.TestCase):
    """Pruebas para el middleware de ayuda."""

    @patch("src.services.help_middleware.HelpService")
    def test_help_context_manager(self, mock_help_service):
        """Prueba el funcionamiento del gestor de contexto HelpContext."""
        # Ejecución: uso básico del gestor de contexto
        with HelpContext(
            user_id="user123",
            help_type=HelpType.RECIPE_SUGGESTION,
            query="¿Qué receta puedo hacer?",
            recipe_id="recipe456"
        ) as ctx:
            ctx.add_response("Puedes hacer pizza")
            ctx.update_context({"ingredientes": ["masa", "tomate", "queso"]})
        
        # Verificación
        mock_help_service.register_help.assert_called_once()
        args = mock_help_service.register_help.call_args[1]
        assert args["user_id"] == "user123"
        assert args["help_type"] == HelpType.RECIPE_SUGGESTION
        assert args["query"] == "¿Qué receta puedo hacer?"
        assert args["response"] == "Puedes hacer pizza"
        assert args["recipe_id"] == "recipe456"
        assert "ingredientes" in args["context_data"]
        assert args["context_data"]["success"] is True

    @patch("src.services.help_middleware.HelpService")
    def test_help_context_with_error(self, mock_help_service):
        """Prueba el gestor de contexto cuando ocurre un error."""
        # Ejecución: simular un error en el bloque with
        try:
            with HelpContext(
                user_id="user123",
                help_type=HelpType.RECIPE_SUGGESTION,
                query="¿Qué receta puedo hacer?",
            ) as ctx:
                ctx.add_response("Procesando...")
                raise ValueError("Error simulado")
        except ValueError:
            pass  # Esperamos que la excepción se propague
        
        # Verificación
        mock_help_service.register_help.assert_called_once()
        args = mock_help_service.register_help.call_args[1]
        assert args["user_id"] == "user123"
        assert args["context_data"]["success"] is False
        assert "error_type" in args["context_data"]
        assert args["context_data"]["error_type"] == "ValueError"
        assert "Error simulado" in args["response"]

    @patch("src.services.help_middleware.HelpService")
    def test_track_help_decorator(self, mock_help_service):
        """Prueba el decorador track_help."""
        # Función de prueba
        @track_help(help_type=HelpType.RECIPE_SUGGESTION, user_id_arg="user_id", recipe_id_arg="recipe_id")
        def suggest_recipe(user_id, recipe_id=None, query=""):
            return "Aquí tienes algunas sugerencias"
        
        # Ejecución
        result = suggest_recipe(user_id="user123", recipe_id="recipe456", query="¿Qué puedo cocinar?")
        
        # Verificación
        assert result == "Aquí tienes algunas sugerencias"
        mock_help_service.register_help.assert_called_once()
        args = mock_help_service.register_help.call_args[1]
        assert args["user_id"] == "user123"
        assert args["recipe_id"] == "recipe456"
        assert args["query"] == "¿Qué puedo cocinar?"
        assert args["help_type"] == HelpType.RECIPE_SUGGESTION

    @patch("src.services.help_middleware.HelpService")
    def test_track_help_decorator_with_error(self, mock_help_service):
        """Prueba el decorador track_help cuando ocurre un error."""
        # Función de prueba que genera un error
        @track_help(help_type=HelpType.RECIPE_SUGGESTION, user_id_arg="user_id")
        def suggest_recipe_error(user_id, query=""):
            raise ValueError("Error en las sugerencias")
        
        # Ejecución
        with pytest.raises(ValueError):
            suggest_recipe_error(user_id="user123", query="¿Qué puedo cocinar?")
        
        # Verificación
        mock_help_service.register_help.assert_called_once()
        args = mock_help_service.register_help.call_args[1]
        assert args["user_id"] == "user123"
        assert args["query"] == "¿Qué puedo cocinar?"
        assert "ERROR" in args["response"]
        assert args["context_data"]["success"] is False

    @patch("src.services.help_middleware.HelpService")
    def test_query_reconstruction(self, mock_help_service):
        """Prueba la reconstrucción de query cuando no se proporciona explícitamente."""
        # Función de prueba sin parámetro query explícito
        @track_help(help_type=HelpType.GENERAL, user_id_arg="user_id")
        def process_command(user_id, command, options=None):
            return f"Procesando {command}"
        
        # Ejecución
        result = process_command(user_id="user123", command="listar", options={"detallado": True})
        
        # Verificación
        mock_help_service.register_help.assert_called_once()
        args = mock_help_service.register_help.call_args[1]
        assert args["user_id"] == "user123"
        # Verificar que se reconstruyó una consulta razonable
        assert "command" in args["query"]
        assert "listar" in args["query"] 