from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from src.api import analysis, health, prompts

app = FastAPI(title="AGENT-DOC", docs_url=None)

app.include_router(health.router)
app.include_router(analysis.router)
app.include_router(prompts.router)


@app.get("/scalar", include_in_schema=False)
def scalar_html():
    return get_scalar_api_reference(openapi_url=app.openapi_url, title=app.title)
