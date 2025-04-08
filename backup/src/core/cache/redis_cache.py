import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

class RedisCache:
    """Mock de caché para pruebas."""
    
    def __init__(self, redis_url: Optional[str] = None):
        """Inicializa el mock de caché."""
        self._cache = {}
        self._expiry = {}
        logger.info("Inicializando mock de caché para pruebas")
    
    def get(self, key: str) -> Any:
        """Obtiene un valor de la caché."""
        if key in self._cache:
            return self._cache[key]
        return None
    
    def set(self, key: str, value: Any, expire: int = 0) -> bool:
        """Establece un valor en la caché."""
        try:
            self._cache[key] = value
            if expire > 0:
                self._expiry[key] = expire
            return True
        except Exception as e:
            logger.error(f"Error al establecer valor en caché: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """Elimina un valor de la caché."""
        if key in self._cache:
            del self._cache[key]
            if key in self._expiry:
                del self._expiry[key]
            return True
        return False
    
    def flush(self) -> bool:
        """Vacía la caché."""
        self._cache = {}
        self._expiry = {}
        return True
