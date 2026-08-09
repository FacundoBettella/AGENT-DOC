from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from src.config import get_settings
from src.constants.agents import CONTEXTUALIZATION_AGENT_NAME
from src.constants.models import GPT4O
from src.infrastructure.tracing.langfuse_tracer import get_langfuse_callback_handler

SYSTEM_PROMPT = (
    "Sos un Analista Legal Senior especializado en derecho contractual, con foco en "
    "comparacion estructural de documentos. Tu unica tarea es comparar la ESTRUCTURA "
    "de un contrato original y su enmienda -- NO los cambios de contenido en si, eso lo "
    "hace otro analista despues de tu trabajo.\n\n"
    "Para cada documento identifica sus secciones o clausulas principales. Despues, "
    "mapea que seccion del original corresponde a que seccion de la enmienda (por "
    "numero, titulo o contenido equivalente), señalando explicitamente:\n"
    "- Secciones nuevas en la enmienda sin equivalente en el original\n"
    "- Secciones del original que no aparecen en la enmienda\n"
    "- Secciones presentes en ambos, con su correspondencia\n\n"
    "Para cada seccion mapeada, describi en una linea su proposito general (de que "
    "trata, no que dice literalmente). No opines sobre que cambio, no resumas el "
    "contenido linea a linea y no saques conclusiones legales -- tu output es un mapa "
    "de referencia estructural para que otro analista lo use como contexto, no un "
    "analisis de cambios."
)

USER_PROMPT_TEMPLATE = (
    "CONTRATO ORIGINAL:\n{original_text}\n\n"
    "ENMIENDA:\n{amendment_text}\n\n"
    "Genera el mapa contextual comparado siguiendo las instrucciones del system prompt."
)


class ContextualizationAgent:
    NAME = CONTEXTUALIZATION_AGENT_NAME

    def __init__(self) -> None:
        settings = get_settings()
        llm = ChatOpenAI(model=GPT4O, temperature=0, api_key=settings.openai_api_key)
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT),
                ("user", USER_PROMPT_TEMPLATE),
            ]
        )
        chain = prompt | llm | StrOutputParser()
        self._chain = chain.with_config({"run_name": self.NAME})

    def build_context_map(self, original_text: str, amendment_text: str) -> str:
        handler = get_langfuse_callback_handler()
        return self._chain.invoke(
            {"original_text": original_text, "amendment_text": amendment_text},
            config={"callbacks": [handler]},
        )
