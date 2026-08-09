# Contratos de prueba

Dos pares de contrato + enmienda, generados sintéticamente con `generate_test_contracts.py` (Pillow) a partir de texto — no son documentos reales, están pensados para ejercitar los distintos tipos de cambio que el sistema debe distinguir (adición, eliminación, modificación).

## Par 1 — `par1_servicios_simple/` (cambios simples)

Contrato de prestación de servicios. La enmienda modifica **únicamente** el monto mensual (USD 1.500 → USD 1.800) y la fecha de vencimiento (30/06/2026 → 31/12/2026). El resto de las cláusulas (Partes, Objeto, Confidencialidad, Jurisdicción) no se repiten en la enmienda y deben interpretarse como **vigentes sin cambios**, no como eliminadas.

Sirve para validar que el sistema no reporta falsos positivos por omisión (una cláusula no repetida ≠ una cláusula eliminada).

## Par 2 — `par2_confidencialidad_compleja/` (cambios complejos)

Contrato de confidencialidad (NDA). La enmienda combina los tres tipos de cambio en un mismo documento:

- **Modificación**: se amplía el alcance territorial (Argentina → Argentina + Uruguay)
- **Eliminación**: se deroga explícitamente la cláusula de restricción de uso (lenguaje explícito: "se eliminan... queda sin efecto")
- **Adición**: se agrega una cláusula nueva de propiedad intelectual

Sirve para validar que el sistema distingue correctamente los tres tipos de cambio dentro de una misma enmienda, y que la eliminación solo se marca cuando hay lenguaje explícito de derogación (no por ausencia física del texto, ver Par 1).

## Regenerar las imágenes

```
docker compose run --rm app python data/test_contracts/generate_test_contracts.py
```

## Resultado esperado (verificado corriendo el pipeline real)

- **Par 1**: `sections_changed` con exactamente 2 entradas (Monto, Vigencia), ambas tipo MODIFICACION.
- **Par 2**: `sections_changed` con exactamente 3 entradas (Alcance Territorial, Restricción de Uso, Propiedad Intelectual), una de cada tipo (MODIFICACION, ELIMINACION, ADICION).
