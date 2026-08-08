import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


class MissingEnvironmentVariableError(RuntimeError):
    def __init__(self, name: str) -> None:
        super().__init__(
            f"Falta la variable de entorno requerida: {name}. "
            f"Revisa tu archivo .env (ver .env.example)."
        )


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    langfuse_public_key: str
    langfuse_secret_key: str
    langfuse_host: str


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise MissingEnvironmentVariableError(name)
    return value


@lru_cache
def get_settings() -> Settings:
    load_dotenv()
    return Settings(
        openai_api_key=_require("OPENAI_API_KEY"),
        langfuse_public_key=_require("LANGFUSE_PUBLIC_KEY"),
        langfuse_secret_key=_require("LANGFUSE_SECRET_KEY"),
        langfuse_host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"),
    )
