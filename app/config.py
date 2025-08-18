import weaviate
from functools import lru_cache
from typing import ClassVar
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.common.constants import HeaderType
from weaviate.client import WeaviateClient


class Configs(BaseSettings):
    BASE_DIR: ClassVar = Path(__file__).resolve().parent.parent
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    DB_USERNAME: str = Field(..., json_schema_extra={"env": "DB_USER"})
    DB_PASSWORD: str = Field(..., json_schema_extra={"env": "DB_PASSWORD"})
    DB_HOST: str = Field(..., json_schema_extra={"env": "DB_HOST"})
    DB_PORT: int = Field(..., json_schema_extra={"env": "DB_PORT"})
    DB_NAME: str = Field(..., json_schema_extra={"env": "DB_NAME"})

    OPENAI_API_KEY: str = Field(..., json_schema_extra={"env": "OPENAI_API_KEY"})
    TAVILY_API_KEY: str = Field(..., json_schema_extra={"env": "TAVILY_API_KEY"})

    WEAVIATE_HTTP_HOST: str = Field(
        ..., json_schema_extra={"env": "WEAVIATE_HTTP_HOST"}
    )
    WEAVIATE_HTTP_PORT: int = Field(
        ..., json_schema_extra={"env": "WEAVIATE_HTTP_PORT"}
    )
    WEAVIATE_GRPC_HOST: str = Field(
        ..., json_schema_extra={"env": "WEAVIATE_GRPC_HOST"}
    )
    WEAVIATE_GRPC_PORT: int = Field(
        ..., json_schema_extra={"env": "WEAVIATE_GRPC_PORT"}
    )

    AGNO_API_KEY: str = Field(..., json_schema_extra={"env": "AGNO_API_KEY"})

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.DB_USERNAME}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def weaviate_client(self) -> WeaviateClient:
        weaviate_client = weaviate.connect_to_custom(
            http_host=config.WEAVIATE_HTTP_HOST,
            http_port=config.WEAVIATE_HTTP_PORT,
            http_secure=False,
            grpc_host=config.WEAVIATE_GRPC_HOST,
            grpc_port=config.WEAVIATE_GRPC_PORT,
            grpc_secure=False,
            headers={HeaderType.X_OPEN_API_KEY: config.OPENAI_API_KEY},
        )
        return weaviate_client


@lru_cache
def get_configs() -> Configs:
    """Get cached settings instance."""
    return Configs()  # type: ignore


config = get_configs()
