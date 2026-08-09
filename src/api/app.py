from fastapi import FastAPI

from src.api import analysis, health, prompts

app = FastAPI(title="AGENT-DOC")

app.include_router(health.router)
app.include_router(analysis.router)
app.include_router(prompts.router)
