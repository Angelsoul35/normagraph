from __future__ import annotations

from fastapi.testclient import TestClient

from normagraph.config import Settings
from normagraph.llm.fake import FailingLLM
from normagraph.service import NormaGraphService


def _service() -> NormaGraphService:
    return NormaGraphService(settings=Settings(), llm=FailingLLM())


def test_service_search_and_detail():
    service = _service()
    hits = service.search("international transfers safeguards")
    assert any(h["norm_id"] == "ART-8" for h in hits)

    detail = service.norm_detail("ART-2")
    assert detail["status"] == "in_force"
    assert "ART-4" in detail["referenced_by"]
    assert "ART-5" in detail["impact"]


def test_service_integrity():
    report = _service().integrity_as_dict()
    assert report["ok"] is False
    kinds = {f["kind"] for f in report["findings"]}
    assert {"dangling_reference", "depends_on_repealed", "orphan"} <= kinds


def test_service_ask_falls_back():
    result = _service().ask("how long to report a breach")
    assert result["source"] == "retrieval"
    assert "ART-7" in result["cited_norms"]


def _client(service):
    import normagraph.main as main

    main._service = service
    return TestClient(main.app)


def test_api_endpoints():
    client = _client(_service())
    assert client.get("/health").json() == {"status": "ok"}

    search = client.get("/search", params={"q": "breach notification"})
    assert search.status_code == 200
    assert search.json()["hits"]

    norm = client.get("/norms/ART-2")
    assert norm.status_code == 200
    assert norm.json()["id"] == "ART-2"

    assert client.get("/norms/NOPE").status_code == 404

    integrity = client.get("/integrity")
    assert integrity.status_code == 200
    assert integrity.json()["ok"] is False

    ask = client.post("/ask", json={"question": "breach reporting deadline"})
    assert ask.status_code == 200
    assert ask.json()["cited_norms"]
