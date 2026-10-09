# Datasets

## `gdpr.jsonl` — the real EU GDPR (Regulation 2016/679)

The 99 articles of the General Data Protection Regulation, used to build and validate
the graph on a real, heavily cross-referential regulation rather than only on the small
hand-made example corpus (see *Validated on the real GDPR* in the top-level README).

**Source.** The GDPRtEXT machine-readable GDPR text
([coolharsh55/GDPRtEXT](https://github.com/coolharsh55/GDPRtEXT), `gdpr.json`), itself
derived from the official EUR-Lex text (CELEX 32016R0679). One JSON line per article:

| Field    | Meaning                                             |
| -------- | --------------------------------------------------- |
| `id`     | the norm id used in the graph, e.g. `Article 6`     |
| `number` | the article number (1–99)                           |
| `title`  | the article heading                                 |
| `text`   | the full article text (its points and sub-points)   |

**How it is used.** `normagraph.real_data.build_gdpr_graph` turns each article into a
`Norm` and every "Article N" citation in an article's text into a `REFERENCES` edge,
recovering the regulation's real dependency web (311 cross-references across the 99
articles). `python -m normagraph.real_benchmark` then reports the structure, a worked
impact query, the integrity findings, and a scramble control.

### Regenerating

```bash
python -c "from normagraph.real_data import fetch_gdpr; print(fetch_gdpr())"
```

Needs outbound access to `raw.githubusercontent.com`. The GDPR text is an official EU
legal document; the GDPRtEXT project's terms apply. Vendored for reproducible
benchmarking only.
