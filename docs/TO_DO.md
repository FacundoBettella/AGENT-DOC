# Pendientes técnicos

Temas que quedaron anotados de la defensa del proyecto como próximos pasos: no son bugs bloqueantes, son mejoras de robustez y costo para cuando el proyecto pase de "demo" a uso más sostenido.

## 1. Validación temprana para no quemar tokens con inputs inválidos

**Problema:** hoy `_validate_document_path()` (`src/infrastructure/parsing/document_parser.py`) solo valida existencia y extensión del archivo — eso corta rápido y gratis los casos obvios (path inexistente, formato no soportado). Pero si los dos archivos son válidos como *archivos* y sin embargo no corresponden entre sí (ej. dos contratos sin relación, o un contrato y una factura), el pipeline no lo detecta hasta después de correr las 4 llamadas a LLM completas (2 parses + 2 agentes) — el desperdicio de tokens ocurre igual, solo que más tarde y más caro.

**Propuesta:** insertar un checkpoint de validación semántica *entre* el parseo (que de todos modos hace falta para tener el texto) y la corrida de los dos agentes, que son la parte cara:

- Un chequeo barato con un modelo económico (`gpt-4o-mini`) que responda sí/no a "¿es plausible que el documento B sea una enmienda o versión modificada del documento A?", corrido con los dos textos ya parseados.
- Si la respuesta es negativa, cortar ahí con una excepción de dominio nueva (ej. `MismatchedDocumentsError`) mapeada a `422 Unprocessable Entity` en la API y a un mensaje claro en `main.py` — evita las 2 llamadas caras a `ContextualizationAgent`/`ExtractionAgent`, que son las que más tokens consumen.
- Documentar en Langfuse este checkpoint como un span propio, para que quede visible en la traza cuándo el pipeline se cortó por esta razón (distinto de un error técnico).

## 2. Economía de tokens: acotar la verbosidad de los agentes

**Problema:** ningún agente tiene un límite explícito de longitud de salida. `ContextualizationAgent` devuelve texto libre sin restricción de formato, y el `description` de `summary_of_the_change` en `ContractChangeOutput` (`src/models.py`) pide explícitamente un "resumen detallado" — eso empuja al modelo hacia prosa larga, no hacia concisión.

**Propuesta:**

- Reescribir el system prompt de `ContextualizationAgent` para pedir formato de lista (un bullet corto por sección), no párrafos narrativos — más fácil de consumir para el Agente 2, además de más barato.
- Ajustar el `Field(description=...)` de `summary_of_the_change` para acotar explícitamente la extensión (ej. "2-3 oraciones, sin repetir el detalle que ya está en `sections_changed`/`topics_touched`") — recordar que esa descripción es parte del contrato que el LLM efectivamente lee vía structured outputs, no es solo documentación.
- Setear un `max_tokens` más ajustado en ambos agentes (hoy solo el parser de Vision lo tiene, vía `MAX_OUTPUT_TOKENS`).
- Medir el impacto real con los datos de tokens que ya reporta cada `GENERATION` en Langfuse (antes/después del cambio de prompt), en vez de asumir la mejora.

## 3. Múltiples clientes concurrentes

**Problema real encontrado al revisar el código:** `POST /analysis` (`src/api/analysis.py`) es una ruta `async def`, pero llama de forma directa (no awaited, no delegada a un threadpool) a `analyze_contract_amendment()`, que es **síncrona** y bloqueante (SDKs síncronos de OpenAI/LangChain). Eso significa que mientras un análisis está en curso, ese request bloquea el event loop de Starlette/FastAPI — con varios usuarios simultáneos, las requests se encolan detrás de la que está corriendo en vez de progresar en paralelo.

Además, sin ningún límite de concurrencia, N usuarios simultáneos disparan hasta N×4 llamadas a la API de OpenAI en paralelo, lo que puede pegar contra el rate limit de la cuenta (`RateLimitError`, ya capturado pero sin reintento).

**Propuesta, en orden de impacto/esfuerzo:**

1. Correr `analyze_contract_amendment()` vía `fastapi.concurrency.run_in_threadpool` (o `asyncio.to_thread`) dentro de la ruta, para dejar de bloquear el event loop con trabajo síncrono de I/O — arregla el problema más urgente con el menor cambio.
2. Acotar cuántos pipelines corren en simultáneo con un semáforo (ej. `anyio.Semaphore`), para no saturar el rate limit de OpenAI cuando hay picos de tráfico.
3. Agregar retry con backoff exponencial ante `RateLimitError` (ej. con `tenacity`) en vez de devolver `502` directo al primer rechazo de la API.
4. Si el volumen crece más, mover la ejecución a un modelo asincrónico real (cola de jobs + polling por `job_id`), en vez de mantener el análisis como un request-response HTTP síncrono de varios segundos.

## 4. Cache de resultados ya calculados

**Problema:** cada corrida de `analyze_contract_amendment()` — vía CLI o vía `/analysis` — re-ejecuta el pipeline completo aunque el par de documentos ya se haya analizado antes con el mismo resultado garantizado (`temperature=0` en todos los agentes).

**Propuesta:**

- Clave de cache: hash del *contenido* de ambos archivos (ej. `sha256(original) + sha256(amendment)`), no del nombre — dos archivos con nombre distinto pero contenido idéntico deben cachear igual, y lo inverso también debe ser cierto.
- Antes de correr el pipeline, calcular esa clave y consultar un store; si hay hit, devolver el resultado guardado sin ninguna llamada a LLM.
- Store: igual que `PromptRepository`, un JSON en `data/` alcanza para el tamaño de este proyecto — no se justifica una base de datos real solo para esto. En un escenario de producción con más volumen, algo tipo Redis con TTL sería lo esperable.
- Matiz a documentar: el cache asume que el *prompt* usado para generar ese resultado no cambió después. Como los prompts son editables en runtime (`PUT /prompts/{agente}`), hay que decidir si la clave de cache también incorpora un hash del prompt vigente al momento de análisis — si no, un cambio de prompt no invalida resultados cacheados con el prompt viejo.
- Bonus: registrar un span/evento `cache_hit` en Langfuse para que la traza muestre explícitamente cuándo una corrida no gastó tokens porque ya existía el resultado.
