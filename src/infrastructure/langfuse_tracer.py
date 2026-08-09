from langfuse import Langfuse, get_client

from src.config import get_settings


def get_langfuse_client() -> Langfuse:
    get_settings()
    return get_client()
