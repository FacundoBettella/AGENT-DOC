import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from src.application.pipeline import analyze_contract_amendment
from src.config import MissingEnvironmentVariableError
from src.infrastructure.agents.extraction_agent import ExtractionError
from src.infrastructure.parsing.document_parser import (
    DocumentValidationError,
    DocxParsingError,
    VisionParsingError,
)
from src.models import ContractChangeOutput

router = APIRouter(prefix="/analysis", tags=["analysis"])


def _save_upload_to_temp(upload: UploadFile) -> Path:
    suffix = Path(upload.filename or "").suffix
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(upload.file.read())
        return Path(tmp.name)


@router.post("", response_model=ContractChangeOutput)
async def analyze(
    original_image: UploadFile = File(...),
    amendment_image: UploadFile = File(...),
) -> ContractChangeOutput:
    original_path = _save_upload_to_temp(original_image)
    amendment_path = _save_upload_to_temp(amendment_image)
    try:
        return analyze_contract_amendment(str(original_path), str(amendment_path))
    except MissingEnvironmentVariableError as error:
        raise HTTPException(status_code=500, detail=str(error)) from error
    except DocumentValidationError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except (VisionParsingError, DocxParsingError, ExtractionError) as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
    finally:
        original_path.unlink(missing_ok=True)
        amendment_path.unlink(missing_ok=True)
