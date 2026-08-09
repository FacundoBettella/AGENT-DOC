from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from src.config import get_settings
from src.constants.agents import CONTEXTUALIZATION_AGENT_NAME
from src.constants.models import GPT4O
from src.infrastructure.prompts.prompt_repository import PromptRepository
from src.infrastructure.tracing.langfuse_tracer import get_langfuse_callback_handler

USER_PROMPT_TEMPLATE = (
    "CONTRATO ORIGINAL:\n{original_text}\n\n"
    "ENMIENDA:\n{amendment_text}\n\n"
    "Genera el mapa contextual comparado siguiendo las instrucciones del system prompt."
)


class ContextualizationAgent:
    NAME = CONTEXTUALIZATION_AGENT_NAME

    def __init__(self, prompt_repository: PromptRepository | None = None) -> None:
        self._prompt_repository = prompt_repository or PromptRepository()
        settings = get_settings()
        llm = ChatOpenAI(model=GPT4O, temperature=0, api_key=settings.openai_api_key)
        system_prompt = self._prompt_repository.get_prompt(self.NAME)
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
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
