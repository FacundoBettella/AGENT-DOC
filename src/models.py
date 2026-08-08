from pydantic import BaseModel, Field


class ContractChangeOutput(BaseModel):
    sections_changed: list[str] = Field(
        ...,
        min_length=1,
        description=(
            "Identificadores de las secciones o clausulas del contrato original "
            "que la enmienda modifico, agrego o elimino (ej. 'Clausula 4.2 - Plazo')."
        ),
    )
    topics_touched: list[str] = Field(
        ...,
        min_length=1,
        description=(
            "Categorias legales o comerciales afectadas por los cambios "
            "(ej. 'Monto', 'Confidencialidad', 'Alcance territorial')."
        ),
    )
    summary_of_the_change: str = Field(
        ...,
        min_length=1,
        description=(
            "Resumen detallado y preciso de que cambio entre el contrato original "
            "y la enmienda, distinguiendo adiciones, eliminaciones y modificaciones."
        ),
    )
