from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from openai import APIError, APITimeoutError, RateLimitError
from pydantic import ValidationError

from src.config import get_settings
from src.infrastructure.tracing.langfuse_tracer import get_langfuse_callback_handler
from src.models import ContractChangeOutput

MODEL_NAME = "gpt-4o"

SYSTEM_PROMPT = (
    "Sos un Auditor Legal especializado en control de cambios contractuales. Tu unica "
    "tarea es identificar, aislar y describir CADA cambio introducido por la enmienda "
    "respecto al contrato original, usando el mapa contextual del analista senior como "
    "guia de donde mirar -- no lo cuestiones, usalo como punto de partida.\n\n"
    "Para cada cambio, distingui explicitamente de que tipo es:\n"
    "- ADICION: contenido nuevo que no existia en el original\n"
    "- ELIMINACION: contenido del original que ya no aparece en la enmienda\n"
    "- MODIFICACION: contenido que existe en ambos pero con valores o texto distinto\n\n"
    "IMPORTANTE sobre ELIMINACION: las enmiendas legales suelen listar UNICAMENTE las "
    "clausulas que cambian, sin reproducir el contrato completo. Que una clausula del "
    "original no aparezca fisicamente en el texto de la enmienda NO significa que fue "
    "eliminada -- sigue vigente tal cual. Marca ELIMINACION solo cuando haya lenguaje "
    "explicito de derogacion (ej. 'se elimina la clausula X', 'queda sin efecto', 'se "
    "deja sin efecto'). Si una clausula del mapa contextual no tiene contraparte en la "
    "enmienda y no hay lenguaje explicito de derogacion, NO la reportes como cambio.\n\n"
    "Reporta unicamente cambios que puedas fundamentar con el texto real de ambos "
    "documentos -- no inventes ni asumas cambios que no esten explicitos en el texto. "
    "Si una seccion mapeada no tiene diferencias reales, no la reportes.\n\n"
    "Completa exactamente estos tres campos:\n"
    "- sections_changed: identificadores de las secciones o clausulas modificadas\n"
    "- topics_touched: categorias legales o comerciales afectadas (ej. Monto, "
    "Confidencialidad, Alcance territorial, Vigencia)\n"
    "- summary_of_the_change: resumen detallado y preciso, distinguiendo adiciones, "
    "eliminaciones y modificaciones"
)

USER_PROMPT_TEMPLATE = (
    "MAPA CONTEXTUAL (del analista senior):\n{context_map}\n\n"
    "CONTRATO ORIGINAL:\n{original_text}\n\n"
    "ENMIENDA:\n{amendment_text}\n\n"
    "Identifica y describi los cambios siguiendo las instrucciones del system prompt."
)


class ExtractionError(RuntimeError):
    pass


class ExtractionAgent:
    def __init__(self) -> None:
        settings = get_settings()
        llm = ChatOpenAI(model=MODEL_NAME, temperature=0, api_key=settings.openai_api_key)
        structured_llm = llm.with_structured_output(ContractChangeOutput)
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                ("user", USER_PROMPT_TEMPLATE),
            ]
        )
        self._chain = prompt | structured_llm

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
