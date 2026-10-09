"""Functional tests for the real GDPR graph.

They prove the vendored data is the real 99-article GDPR, that the graph recovers the
regulation's real cross-references (pinned against a hand-checked article), that the
queries answer correctly on real data, and that the edges are the real citations
(scrambling the text collapses them).
"""

from __future__ import annotations

import json

import pytest

from normagraph.analysis import analyze
from normagraph.real_benchmark import format_report, run_benchmark
from normagraph.real_data import (
    build_gdpr_graph,
    extract_references,
    load_gdpr,
)


@pytest.fixture(scope="module")
def articles():
    return load_gdpr()


@pytest.fixture(scope="module")
def graph(articles):
    return build_gdpr_graph(articles)


@pytest.fixture(scope="module")
def report(articles):
    return run_benchmark(articles)


def test_loads_the_real_gdpr(articles):
    assert len(articles) == 99  # the GDPR has 99 articles
    numbers = sorted(a["number"] for a in articles)
    assert numbers == list(range(1, 100))
    for a in articles:
        assert a["id"] == f"Article {a['number']}"
        assert a["title"] and a["text"]


def test_graph_recovers_real_cross_references(graph):
    assert len(graph.norms) == 99
    assert len(graph.relations) > 250  # a dense real citation web
    # Pinned ground truth: Article 6(4) cites Articles 9, 10 and 23 (hand-checked).
    assert sorted(graph.references_of("Article 6"), key=lambda s: int(s.split()[1])) == [
        "Article 9",
        "Article 10",
        "Article 23",
    ]
    # Article 5 (processing principles) is foundational: many articles cite it.
    assert len(graph.referenced_by("Article 5")) >= 3


def test_extract_references_handles_single_range_and_list():
    valid = set(range(1, 100))
    assert extract_references("subject to Article 9 and Article 23", valid) == {9, 23}
    assert extract_references("in accordance with Articles 44 to 47", valid) == {44, 45, 46, 47}
    assert extract_references("see Article 999", valid) == set()  # not a real article


def test_impact_query_is_large_for_a_foundational_article(graph):
    impact = graph.impact_of("Article 5")
    assert len(impact) >= 40  # a huge transitive blast radius on the real corpus


def test_integrity_findings_are_real_orphans(graph):
    report = analyze(graph)
    orphans = report.by_kind("orphan")
    assert len(orphans) >= 5  # articles with no explicit article-to-article citation
    # Every orphan genuinely has no reference edge in either direction.
    for finding in orphans:
        nid = finding.norm_id
        assert not graph.references_of(nid) and not graph.referenced_by(nid)


def test_report_metrics_and_scramble_control(report):
    assert report.n_articles == 99
    assert report.n_references > 250
    assert report.resolution_rate == 1.0  # every extracted citation hits a real article
    assert report.impact_example_size >= 40
    # Scrambling each article's words destroys the "Article N" adjacencies.
    assert report.scrambled_references < report.n_references * 0.1
    assert report.edges_are_real


def test_format_report_renders(report):
    text = format_report(report)
    assert "GDPR" in text
    assert "cross-references" in text
    assert str(report.n_references) in text


def test_main_prints(capsys):
    from normagraph.real_benchmark import main

    main()
    assert "real-data benchmark" in capsys.readouterr().out


def test_loader_rejects_missing(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_gdpr(tmp_path / "nope.jsonl")


def test_fetch_parses_and_writes(tmp_path, monkeypatch):
    import normagraph.real_data as rd

    fake = {
        "chapters": [
            {
                "number": "I",
                "type": "chapter",
                "contents": [
                    {
                        "number": "1",
                        "title": "Subject-matter",
                        "type": "article",
                        "contents": [
                            {"number": "1", "type": "point",
                             "text": "This Regulation refers to Article 2.", "subpoints": []},
                        ],
                    },
                    {
                        "number": "2",
                        "title": "Scope",
                        "type": "article",
                        "contents": [
                            {"number": "1", "type": "point",
                             "text": "Scope text.", "subpoints": []},
                        ],
                    },
                ],
            }
        ]
    }
    monkeypatch.setattr(rd, "urlopen", lambda url, timeout=60.0: json.dumps(fake).encode())
    dest = tmp_path / "gdpr.jsonl"
    n = rd.fetch_gdpr(dest)
    assert n == 2
    arts = rd.load_gdpr(dest)
    assert [a["id"] for a in arts] == ["Article 1", "Article 2"]
    g = rd.build_gdpr_graph(arts)
    assert g.references_of("Article 1") == ["Article 2"]  # the real citation was parsed
