import contextvars
from concurrent.futures import ThreadPoolExecutor

from src.infrastructure.agents.contextualization_agent import ContextualizationAgent
from src.infrastructure.agents.extraction_agent import ExtractionAgent
from src.infrastructure.parsing.document_parser import parse_contract_document
from src.infrastructure.tracing.langfuse_tracer import get_langfuse_client
from src.models import ContractChangeOutput

ROOT_TRACE_NAME = "contract-analysis"
PARSE_ORIGINAL_SPAN_NAME = "parse_original_contract"
PARSE_AMENDMENT_SPAN_NAME = "parse_amendment_contract"


def _parse_with_span(document_path: str, span_name: str) -> str:
    langfuse = get_langfuse_client()
    with langfuse.start_as_current_observation(as_type="span", name=span_name) as span:
        text = parse_contract_document(document_path)
        span.update(output=text)
    return text


def analyze_contract_amendment(
    original_path: str, amendment_path: str
) -> ContractChangeOutput:
    langfuse = get_langfuse_client()

    with langfuse.start_as_current_observation(
        as_type="span", name=ROOT_TRACE_NAME
    ) as root_span:
        root_span.update(
            input={
                "original_path": original_path,
                "amendment_path": amendment_path,
            }
        )
        try:
            # Se copia el contextvars context (que ya tiene a root_span como
            # "current span") antes de cada submit, para que los spans hijos
            # abiertos dentro de cada hilo cuelguen del span raiz en Langfuse.
            with ThreadPoolExecutor(max_workers=2) as executor:
                original_future = executor.submit(
                    contextvars.copy_context().run,
                    _parse_with_span,
                    original_path,
                    PARSE_ORIGINAL_SPAN_NAME,
                )
                amendment_future = executor.submit(
                    contextvars.copy_context().run,
                    _parse_with_span,
                    amendment_path,
                    PARSE_AMENDMENT_SPAN_NAME,
                )
                original_text = original_future.result()
                amendment_text = amendment_future.result()

            context_map = ContextualizationAgent().build_context_map(
                original_text, amendment_text
            )
            result = ExtractionAgent().extract_changes(
                context_map, original_text, amendment_text
            )

            root_span.update(output=result.model_dump())
        except Exception as error:
            root_span.update(level="error", status_message=str(error))
            raise
        finally:
            langfuse.flush()

    return result
