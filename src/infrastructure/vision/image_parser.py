import base64
from pathlib import Path

from openai import APIError, APITimeoutError, RateLimitError

from src.infrastructure.vision.openai_client import get_openai_client

VALID_EXTENSIONS = {".jpg", ".jpeg", ".png"}
VISION_MODEL = "gpt-4o"
MAX_OUTPUT_TOKENS = 4096

SYSTEM_PROMPT = (
    "Sos un asistente experto en digitalizar documentos legales. Tu unica tarea es "
    "transcribir fielmente el texto completo de la imagen de un contrato, preservando "
    "la jerarquia original: numeracion de clausulas, secciones, subsecciones, titulos "
    "y parrafos. No resumas, no interpretes, no agregues comentarios ni corrijas "
    "errores del documento original. Si una parte es ilegible, marcala como [ILEGIBLE] "
    "en vez de inventar contenido."
)


class ImageValidationError(ValueError):
    pass


class VisionParsingError(RuntimeError):
    pass


def _validate_image_path(image_path: str) -> Path:
    path = Path(image_path)
    if not path.exists():
        raise ImageValidationError(f"El archivo no existe: {image_path}")
    if not path.is_file():
        raise ImageValidationError(f"La ruta no es un archivo: {image_path}")
    if path.suffix.lower() not in VALID_EXTENSIONS:
        valid = ", ".join(sorted(VALID_EXTENSIONS))
        raise ImageValidationError(
            f"Formato no soportado ({path.suffix}). Formatos validos: {valid}"
        )
    return path


def _encode_image_base64(path: Path) -> str:
    with path.open("rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def _mime_type(path: Path) -> str:
    return "image/png" if path.suffix.lower() == ".png" else "image/jpeg"


def parse_contract_image(image_path: str) -> str:
    path = _validate_image_path(image_path)
    encoded_image = _encode_image_base64(path)
    mime = _mime_type(path)

    client = get_openai_client()
    try:
        response = client.chat.completions.create(
            model=VISION_MODEL,
            temperature=0,
            max_tokens=MAX_OUTPUT_TOKENS,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Transcribi el texto completo de este contrato.",
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime};base64,{encoded_image}"},
                        },
                    ],
                },
            ],
        )
    except RateLimitError as error:
        raise VisionParsingError(
            f"Limite de rate excedido al parsear {path.name}: {error}"
        ) from error
    except APITimeoutError as error:
        raise VisionParsingError(f"Timeout al parsear {path.name}: {error}") from error
    except APIError as error:
        raise VisionParsingError(
            f"Error de la API de OpenAI al parsear {path.name}: {error}"
        ) from error

    text = response.choices[0].message.content
    if not text or not text.strip():
        raise VisionParsingError(f"El modelo no devolvio texto para {path.name}")
    return text.strip()
