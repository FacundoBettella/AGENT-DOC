from langfuse import Langfuse, get_client
from langfuse.langchain import CallbackHandler

from src.config import get_settings


def get_langfuse_client() -> Langfuse:
    get_settings()
    return get_client()


def get_langfuse_callback_handler() -> CallbackHandler:
    get_settings()
    return CallbackHandler()
