import logging
import sys
from typing import Optional
from datetime import datetime

from .config import settings

def setup_logging(
    level: Optional[str] = None,
    log_format: Optional[str] = None
) -> None:
    """Configure logging for the application.

    Args:
        level: Logging level (default: from settings)
        log_format: Log format string (default: from settings)
    """
    # Set level and format from settings if not provided
    level = level or settings.LOG_LEVEL
    log_format = log_format or settings.LOG_FORMAT

    # Configure root logger
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(f'logs/app_{datetime.now().strftime("%Y%m%d")}.log')
        ]
    )

    # Configure third-party loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("redis").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    # Create logger for this module
    logger = logging.getLogger(__name__)
    logger.info("Logging configured successfully")

# Create logger instance
logger = logging.getLogger(__name__) 