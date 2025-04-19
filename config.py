import os
import logging
from pathlib import Path

# Configuración de rutas básicas
BASE_DIR = Path(__file__).parent.absolute()
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Crear directorios necesarios si no existen
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Cargar variables de entorno
from dotenv import load_dotenv
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
USDA_API_KEY = os.getenv("USDA_API_KEY", "")

# Configuración de la aplicación
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
PORT = int(os.getenv("PORT", "8080"))
MOCK_DB = os.getenv("MOCK_DB", "True").lower() in ("true", "1", "t")

# Configuración del modelo
MODEL_CONFIG = {
    "model": os.getenv("MODEL_NAME", "gpt-3.5-turbo"),
    "temperature": float(os.getenv("MODEL_TEMPERATURE", "0.7")),
    "max_tokens": int(os.getenv("MODEL_MAX_TOKENS", "1000")),
    "api_key": OPENAI_API_KEY
}

# Configurar logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOGS_DIR / 'app.log')
    ]
)

# Validar configuración crítica
if not OPENAI_API_KEY or OPENAI_API_KEY == "sk-demo-key1234567890abcdef":
    logging.warning("ADVERTENCIA: OPENAI_API_KEY no configurada correctamente") 