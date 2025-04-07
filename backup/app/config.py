from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import BaseModel, Field

class Settings(BaseSettings):
    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    DEBUG: bool = Field(default=False, env="DEBUG")

    # Redis Configuration
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")

    # USDA API Configuration
    USDA_API_KEY: str = Field(..., env="USDA_API_KEY")
    USDA_API_URL: str = Field(
        default="https://api.nal.usda.gov/fdc/v1",
        env="USDA_API_URL"
    )

    # Monitoring Configuration
    PROMETHEUS_MULTIPROC_DIR: str = Field(
        default="/tmp",
        env="PROMETHEUS_MULTIPROC_DIR"
    )
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")

    # Logging Configuration
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )

    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        env="ACCESS_TOKEN_EXPIRE_MINUTES"
    )

    class Config:
        env_file = ".env"
        case_sensitive = True

class RedisConfig(BaseModel):
    host: str
    port: int
    db: int = 0
    password: Optional[str] = None
    ssl: bool = False

    @classmethod
    def from_url(cls, url: str) -> "RedisConfig":
        """Create RedisConfig from URL string."""
        # Parse URL components
        parts = url.split("://")
        if len(parts) != 2:
            raise ValueError("Invalid Redis URL format")

        scheme, rest = parts
        if scheme not in ("redis", "rediss"):
            raise ValueError("Invalid Redis URL scheme")

        # Parse host and port
        host_port, *rest = rest.split("/")
        host, *port = host_port.split(":")
        port = int(port[0]) if port else 6379

        # Parse database
        db = int(rest[0]) if rest else 0

        # Parse password if present
        password = None
        if "@" in host:
            password, host = host.split("@")

        return cls(
            host=host,
            port=port,
            db=db,
            password=password,
            ssl=(scheme == "rediss")
        )

settings = Settings()
redis_config = RedisConfig.from_url(settings.REDIS_URL) 