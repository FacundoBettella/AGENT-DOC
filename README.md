# AGENT-DOC

Sistema multi-agente que compara un contrato original y su enmienda (imágenes escaneadas), usando GPT-4o Vision para extraer el texto y dos agentes de LangChain que colaboran para identificar los cambios legales. La salida es un JSON validado con Pydantic, y cada paso queda trazado en Langfuse.

Proyecto para LegalMove (contexto ficticio: empresa legaltech que procesa miles de enmiendas de contratos por mes) — módulo de AI Engineering.

## Quickstart

Requiere Docker Desktop.

```bash
git clone https://github.com/FacundoBettella/AGENT-DOC.git
cd AGENT-DOC
cp .env.example .env
# completar OPENAI_API_KEY, LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY en .env
docker compose build

docker compose run --rm app python -m src.main \
  data/test_contracts/par1_servicios_simple/original.png \
  data/test_contracts/par1_servicios_simple/amendment.png
```

## Documentación

- [Arquitectura](docs/ARCHITECTURE.md) — diagramas, estructura de carpetas, cómo funciona el pipeline, decisiones técnicas
- [API](docs/API.md) — endpoints, ABM de prompts, Scalar/Postman
- [Contratos de prueba](data/test_contracts/README.md)

## Stack técnico

Python 3.12 · FastAPI · OpenAI GPT-4o (Vision + Chat) · LangChain / langchain-openai · Pydantic v2 · Langfuse v4 · python-dotenv · Docker / Docker Compose
