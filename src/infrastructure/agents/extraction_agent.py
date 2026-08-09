from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from openai import APIError, APITimeoutError, RateLimitError
from pydantic import ValidationError

from src.config import get_settings
from src.constants.agents import EXTRACTION_AGENT_NAME
from src.constants.models import GPT4O
from src.infrastructure.prompts.prompt_repository import PromptRepository
from src.infrastructure.tracing.langfuse_tracer import get_langfuse_callback_handler
from src.models import ContractChangeOutput

USER_PROMPT_TEMPLATE = (
    "MAPA CONTEXTUAL (del analista senior):\n{context_map}\n\n"
    "CONTRATO ORIGINAL:\n{original_text}\n\n"
    "ENMIENDA:\n{amendment_text}\n\n"
    "Identifica y describi los cambios siguiendo las instrucciones del system prompt."
)


class ExtractionError(RuntimeError):
    pass


class ExtractionAgent:
    NAME = EXTRACTION_AGENT_NAME

    def __init__(self, prompt_repository: PromptRepository | None = None) -> None:
        self._prompt_repository = prompt_repository or PromptRepository()
        settings = get_settings()
        llm = ChatOpenAI(model=GPT4O, temperature=0, api_key=settings.openai_api_key)
        structured_llm = llm.with_structured_output(ContractChangeOutput)
        system_prompt = self._prompt_repository.get_prompt(self.NAME)
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("user", USER_PROMPT_TEMPLATE),
            ]
        )
        chain = prompt | structured_llm
        self._chain = chain.with_config({"run_name": self.NAME})

    def extract_changes(
        self, context_map: str, original_text: str, amendment_text: str
    ) -> ContractChangeOutput:
        handler = get_langfuse_callback_handler()
        try:
            result = self._chain.invoke(
                {
                    "context_map": context_map,
                    "original_text": original_text,
                    "amendment_text": amendment_text,
                },
                config={"callbacks": [handler]},
            )
        except RateLimitError as error:
            raise ExtractionError(
                f"Limite de rate excedido en ExtractionAgent: {error}"
            ) from error
        except APITimeoutError as error:
            raise ExtractionError(f"Timeout en ExtractionAgent: {error}") from error
        except APIError as error:
            raise ExtractionError(
                f"Error de la API de OpenAI en ExtractionAgent: {error}"
            ) from error
        except ValidationError as error:
            raise ExtractionError(
                f"El output del modelo no cumplio el schema esperado: {error}"
            ) from error

        if not isinstance(result, ContractChangeOutput):
            raise ExtractionError(f"El modelo devolvio un tipo inesperado: {type(result)!r}")
        return result
