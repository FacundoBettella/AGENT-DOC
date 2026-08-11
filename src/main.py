import argparse
import sys

from src.application.pipeline import analyze_contract_amendment
from src.config import MissingEnvironmentVariableError
from src.infrastructure.agents.extraction_agent import ExtractionError
from src.infrastructure.parsing.document_parser import (
    DocumentValidationError,
    DocxParsingError,
    VisionParsingError,
)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-doc",
        description=(
            "Compara un contrato original y su enmienda (imagen escaneada JPEG/PNG o "
            "documento Word) y devuelve un JSON con los cambios detectados."
        ),
    )
    parser.add_argument("original_image", help="Path al contrato original (JPEG/PNG/DOCX)")
    parser.add_argument("amendment_image", help="Path a la enmienda (JPEG/PNG/DOCX)")
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()

    try:
        result = analyze_contract_amendment(args.original_image, args.amendment_image)
    except MissingEnvironmentVariableError as error:
        print(f"Error de configuracion: {error}", file=sys.stderr)
        return 1
    except DocumentValidationError as error:
        print(f"Error de input: {error}", file=sys.stderr)
        return 1
    except (VisionParsingError, DocxParsingError, ExtractionError) as error:
        print(f"Error al procesar con el modelo: {error}", file=sys.stderr)
        return 1

    print(result.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
