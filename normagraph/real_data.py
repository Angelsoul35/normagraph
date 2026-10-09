"""Build the graph from a real regulation: the EU GDPR.

The bundled corpus (:mod:`normagraph.data`) is a small hand-made example, ideal for
deterministic tests. This module builds the same graph from a **real**, heavily
cross-referential regulation — Regulation (EU) 2016/679 (the GDPR), 99 articles whose
text cites one another ("...as referred to in Article 6", "pursuant to Article 9(2)").
Each article becomes a :class:`~normagraph.norms.Norm`; every "Article N" citation in an
article's text becomes a ``REFERENCES`` edge, so the real regulation's dependency web is
recovered automatically and the graph queries (impact, references, integrity) run on it.

Source: the GDPRtEXT machine-readable GDPR text
(https://github.com/coolharsh55/GDPRtEXT, ``gdpr.json``). A snapshot is vendored under
``datasets/gdpr.jsonl``; :func:`fetch_gdpr` refreshes it.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from .graph import NormGraph
from .norms import Norm, Relation, RelationType, Status

_REPO_ROOT = Path(__file__).resolve().parents[1]
_DATASET_PATH = _REPO_ROOT / "datasets" / "gdpr.jsonl"
_GDPR_URL = "https://raw.githubusercontent.com/coolharsh55/GDPRtEXT/master/gdpr.json"

_ARTICLE_RE = re.compile(r"\bArticles?\s+(\d+)(?:\s*(?:to|and|,|\s)+(\d+))?", re.IGNORECASE)


def article_id(number: int | str) -> str:
    return f"Article {number}"


def _article_text(node: dict) -> str:
    """Concatenate the text of an article's points and sub-points."""
    parts: list[str] = []
    if isinstance(node, dict):
        if node.get("text"):
            parts.append(str(node["text"]))
        for key in ("contents", "points", "subpoints"):
            for child in node.get(key, []) or []:
                parts.append(_article_text(child))
    return " ".join(p for p in parts if p).strip()


def _walk_articles(node: dict, out: list[dict]) -> None:
    if isinstance(node, dict):
        if node.get("type") == "article":
            out.append(node)
        for child in node.get("contents", []) or []:
            _walk_articles(child, out)


def extract_references(text: str, valid: set[int]) -> set[int]:
    """Return the set of article numbers cited in ``text`` that exist in the corpus.

    Handles single citations ("Article 6"), ranges ("Articles 44 to 49"), and lists
    ("Articles 6 and 9"); a range expands to every article in it. Only numbers that are
    real articles (in ``valid``) are kept.
    """
    found: set[int] = set()
    for lo, hi in _ARTICLE_RE.findall(text):
        a = int(lo)
        if hi:
            b = int(hi)
            if b > a and b - a <= 30:  # a genuine range, not two unrelated cites
                found.update(range(a, b + 1))
            else:
                found.update({a, b})
        else:
            found.add(a)
    return {n for n in found if n in valid}


def load_gdpr(path: str | Path | None = None) -> list[dict]:
    """Return the vendored GDPR articles as ``[{id, number, title, text}, ...]``."""
    target = Path(path) if path is not None else _DATASET_PATH
    if not target.exists():
        raise FileNotFoundError(
            f"Vendored GDPR not found at {target}. Refresh it with "
            "normagraph.real_data.fetch_gdpr()."
        )
    articles = []
    for line in target.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            articles.append(json.loads(line))
    return articles


def build_gdpr_graph(articles: list[dict] | None = None) -> NormGraph:
    """Build a :class:`NormGraph` of the real GDPR: an article per norm, a citation
    per ``REFERENCES`` edge."""
    articles = articles if articles is not None else load_gdpr()
    numbers = {int(a["number"]) for a in articles}
    norms = [
        Norm(id=a["id"], title=a["title"], text=a["text"], status=Status.IN_FORCE)
        for a in articles
    ]
    relations: list[Relation] = []
    for a in articles:
        src_num = int(a["number"])
        for target in sorted(extract_references(a["text"], numbers)):
            if target != src_num:
                relations.append(
                    Relation(a["id"], article_id(target), RelationType.REFERENCES)
                )
    return NormGraph(norms, relations)


def _default_urlopen(url: str, timeout: float = 60.0) -> bytes:
    import urllib.request

    with urllib.request.urlopen(url, timeout=timeout) as response:  # noqa: S310 (trusted host)
        return response.read()


urlopen = _default_urlopen


def fetch_gdpr(path: str | Path | None = None) -> int:
    """Download the real GDPR text and vendor it as ``datasets/gdpr.jsonl``.

    Returns the number of articles written. Monkeypatch
    :data:`normagraph.real_data.urlopen` to exercise this offline.
    """
    target = Path(path) if path is not None else _DATASET_PATH
    raw = urlopen(_GDPR_URL)
    doc = json.loads(raw)
    articles: list[dict] = []
    for chapter in doc.get("chapters", []):
        _walk_articles(chapter, articles)

    target.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with target.open("w", encoding="utf-8") as handle:
        for art in articles:
            text = _article_text(art)
            if not text:
                continue
            handle.write(
                json.dumps(
                    {
                        "id": article_id(art["number"]),
                        "number": int(art["number"]),
                        "title": art.get("title", "").strip(),
                        "text": text,
                    }
                )
                + "\n"
            )
            n += 1
    return n
