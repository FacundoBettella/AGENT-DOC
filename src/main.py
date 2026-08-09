import argparse
import sys

from src.application.pipeline import analyze_contract_amendment
from src.config import MissingEnvironmentVariableError
from src.infrastructure.agents.extraction_agent import ExtractionError
from src.infrastructure.vision.image_parser import ImageValidationError, VisionParsingError


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-doc",
        description=(
            "Compara un contrato original y su enmienda a partir de imagenes escaneadas "
            "y devuelve un JSON con los cambios detectados."
        ),
    )
    parser.add_argument("original_image", help="Path a la imagen del contrato original (JPEG/PNG)")
    parser.add_argument("amendment_image", help="Path a la imagen de la enmienda (JPEG/PNG)")
    return parser


def main() -> int:
    args = build_arg_parser().parse_args()

    try:
        result = analyze_contract_amendment(args.original_image, args.amendment_image)
    except MissingEnvironmentVariableError as error:
        print(f"Error de configuracion: {error}", file=sys.stderr)
        return 1
    except ImageValidationError as error:
        print(f"Error de input: {error}", file=sys.stderr)
        return 1
    except (VisionParsingError, ExtractionError) as error:
        print(f"Error al procesar con el modelo: {error}", file=sys.stderr)
        return 1

    print(result.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
