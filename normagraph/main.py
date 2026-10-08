"""NormaGraph HTTP API."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .service import NormaGraphService

app = FastAPI(
    title="NormaGraph",
    version="1.0.0",
    summary="A knowledge graph of regulations with cross-reference analysis.",
)

_service: NormaGraphService | None = None


def get_service() -> NormaGraphService:
    global _service
    if _service is None:
        _service = NormaGraphService()
    return _service


class AskRequest(BaseModel):
    question: str = Field(min_length=1)


@app.get("/health", tags=["ops"])
def health() -> dict:
    return {"status": "ok"}


@app.get("/search", tags=["graph"])
def search(q: str) -> dict:
    return {"query": q, "hits": get_service().search(q)}


@app.get("/norms/{norm_id}", tags=["graph"])
def norm_detail(norm_id: str) -> dict:
    detail = get_service().norm_detail(norm_id)
    if detail is None:
        raise HTTPException(status_code=404, detail=f"unknown norm: {norm_id}")
    return detail


@app.get("/integrity", tags=["analysis"])
def integrity() -> dict:
    return get_service().integrity_as_dict()


@app.post("/ask", tags=["qa"])
def ask(request: AskRequest) -> dict:
    return get_service().ask(request.question)
