from src.infrastructure.agents.contextualization_agent import ContextualizationAgent
from src.infrastructure.agents.extraction_agent import ExtractionAgent
from src.infrastructure.tracing.langfuse_tracer import get_langfuse_client
from src.infrastructure.vision.image_parser import parse_contract_image
from src.models import ContractChangeOutput

ROOT_TRACE_NAME = "contract-analysis"
PARSE_ORIGINAL_SPAN_NAME = "parse_original_contract"
PARSE_AMENDMENT_SPAN_NAME = "parse_amendment_contract"


def analyze_contract_amendment(
    original_image_path: str, amendment_image_path: str
) -> ContractChangeOutput:
    langfuse = get_langfuse_client()

    with langfuse.start_as_current_observation(
        as_type="span", name=ROOT_TRACE_NAME
    ) as root_span:
        root_span.update(
            input={
                "original_image_path": original_image_path,
                "amendment_image_path": amendment_image_path,
            }
        )
        try:
            with langfuse.start_as_current_observation(
                as_type="span", name=PARSE_ORIGINAL_SPAN_NAME
            ) as span:
                original_text = parse_contract_image(original_image_path)
                span.update(output=original_text)

            with langfuse.start_as_current_observation(
                as_type="span", name=PARSE_AMENDMENT_SPAN_NAME
            ) as span:
                amendment_text = parse_contract_image(amendment_image_path)
                span.update(output=amendment_text)

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
