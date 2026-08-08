from fastapi import FastAPI

app = FastAPI(title="AGENT-DOC")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
