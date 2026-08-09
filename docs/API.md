# API

```bash
docker compose up
```

## Analizar un contrato

```bash
curl -X POST http://localhost:8000/analysis \
  -F "original_image=@data/test_contracts/par1_servicios_simple/original.png" \
  -F "amendment_image=@data/test_contracts/par1_servicios_simple/amendment.png"
```

Documentación interactiva: `http://localhost:8000/scalar` (Scalar).
Para Postman: `File → Import → Link` con `http://localhost:8000/openapi.json`, o importar directamente el archivo `openapi.json` de este repo.

## Gestión de prompts (ABM)

Los system prompts de los dos agentes se pueden leer y editar en runtime sin reiniciar la app (persisten en `data/prompts.json`, sembrado con valores default en el primer arranque):

```bash
curl http://localhost:8000/prompts
curl http://localhost:8000/prompts/extraction_agent
curl -X PUT http://localhost:8000/prompts/extraction_agent \
  -H "Content-Type: application/json" \
  -d '{"system_prompt": "..."}'
```

## CLI (alternativa a la API)

```bash
docker compose run --rm app python -m src.main <path-original> <path-enmienda>
```
