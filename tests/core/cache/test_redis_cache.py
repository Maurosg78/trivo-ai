import json
import unittest
from unittest.mock import patch, Mock

import redis
from pydantic import BaseModel

from src.core.cache.redis_cache import RedisCache


class TestUser(BaseModel):
    """Modelo de prueba para verificar la serialización."""
    name: str
    age: int


class TestRedisCache(unittest.TestCase):
    """Prueba para el servicio RedisCache."""

    @patch('redis.Redis')
    def setUp(self, mock_redis):
        """Configurar recursos para las pruebas."""
        # Configurar el objeto mock para Redis
        self.mock_redis_client = Mock()
        mock_redis.return_value = self.mock_redis_client
        
        # Crear instancia del servicio
        self.cache = RedisCache()

    def test_get_value_exists(self):
        """Prueba la obtención de un valor existente."""
        # Configurar mock para simular un valor en la caché
        test_data = json.dumps({"name": "John", "age": 30})
        self.mock_redis_client.get.return_value = test_data
        
        # Obtener valor
        result = self.cache.get("test_key")
        
        # Verificar resultados
        self.mock_redis_client.get.assert_called_once_with("test_key")
        self.assertEqual(result, {"name": "John", "age": 30})

    def test_get_value_not_exists(self):
        """Prueba la obtención de un valor que no existe."""
        # Configurar mock para simular que no hay valor
        self.mock_redis_client.get.return_value = None
        
        # Obtener valor
        result = self.cache.get("test_key")
        
        # Verificar resultados
        self.mock_redis_client.get.assert_called_once_with("test_key")
        self.assertIsNone(result)

    def test_get_value_error(self):
        """Prueba la obtención de un valor cuando ocurre un error."""
        # Configurar mock para simular un error
        self.mock_redis_client.get.side_effect = Exception("Error de conexión")
        
        # Obtener valor
        result = self.cache.get("test_key")
        
        # Verificar resultados
        self.mock_redis_client.get.assert_called_once_with("test_key")
        self.assertIsNone(result)

    def test_set_value_success(self):
        """Prueba el almacenamiento exitoso de un valor."""
        # Configurar mock
        self.mock_redis_client.setex.return_value = True
        
        # Almacenar valor
        result = self.cache.set("test_key", {"name": "John", "age": 30}, expire=600)
        
        # Verificar resultados
        self.mock_redis_client.setex.assert_called_once_with("test_key", 600, json.dumps({"name": "John", "age": 30}))
        self.assertTrue(result)

    def test_set_value_pydantic(self):
        """Prueba el almacenamiento de un modelo Pydantic."""
        # Configurar mock
        self.mock_redis_client.setex.return_value = True
        
        # Crear modelo de prueba
        test_user = TestUser(name="John", age=30)
        
        # Almacenar valor
        result = self.cache.set("test_key", test_user, expire=600)
        
        # Verificar resultados
        self.mock_redis_client.setex.assert_called_once_with("test_key", 600, json.dumps({"name": "John", "age": 30}))
        self.assertTrue(result)

    def test_set_value_error(self):
        """Prueba el almacenamiento cuando ocurre un error."""
        # Configurar mock para simular un error
        self.mock_redis_client.setex.side_effect = Exception("Error de conexión")
        
        # Almacenar valor
        result = self.cache.set("test_key", {"name": "John", "age": 30})
        
        # Verificar resultados
        self.assertFalse(result)

    def test_delete_value_success(self):
        """Prueba la eliminación exitosa de un valor."""
        # Configurar mock
        self.mock_redis_client.delete.return_value = 1
        
        # Eliminar valor
        result = self.cache.delete("test_key")
        
        # Verificar resultados
        self.mock_redis_client.delete.assert_called_once_with("test_key")
        self.assertTrue(result)

    def test_delete_value_error(self):
        """Prueba la eliminación cuando ocurre un error."""
        # Configurar mock para simular un error
        self.mock_redis_client.delete.side_effect = Exception("Error de conexión")
        
        # Eliminar valor
        result = self.cache.delete("test_key")
        
        # Verificar resultados
        self.assertFalse(result)

    def test_exists_value_present(self):
        """Prueba la verificación de existencia cuando el valor existe."""
        # Configurar mock
        self.mock_redis_client.exists.return_value = 1
        
        # Verificar existencia
        result = self.cache.exists("test_key")
        
        # Verificar resultados
        self.mock_redis_client.exists.assert_called_once_with("test_key")
        self.assertTrue(result)

    def test_exists_value_not_present(self):
        """Prueba la verificación de existencia cuando el valor no existe."""
        # Configurar mock
        self.mock_redis_client.exists.return_value = 0
        
        # Verificar existencia
        result = self.cache.exists("test_key")
        
        # Verificar resultados
        self.mock_redis_client.exists.assert_called_once_with("test_key")
        self.assertFalse(result)

    def test_exists_error(self):
        """Prueba la verificación de existencia cuando ocurre un error."""
        # Configurar mock para simular un error
        self.mock_redis_client.exists.side_effect = Exception("Error de conexión")
        
        # Verificar existencia
        result = self.cache.exists("test_key")
        
        # Verificar resultados
        self.assertFalse(result) 