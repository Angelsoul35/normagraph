"""NormaGraph command-line demo."""

from __future__ import annotations

import argparse

from .service import NormaGraphService


def demo() -> None:
    print("1) Building the norm graph ...")
    service = NormaGraphService()
    print(f"   {len(service.graph.norms)} norms, {len(service.graph.relations)} relationships")

    print("2) Searching for 'breach notification' (text match + graph neighbours):")
    for hit in service.search("breach notification deadline"):
        print(f"   [{hit['via']:5}] {hit['norm_id']:9} {hit['title']}  (score {hit['score']})")

    print("3) Impact of changing ART-2 (Definitions) — everything that depends on it:")
    detail = service.norm_detail("ART-2")
    print(f"   referenced_by: {detail['referenced_by']}")
    print(f"   full impact:   {detail['impact']}")

    print("4) Integrity check of the corpus:")
    report = service.integrity_as_dict()
    print(f"   ok: {report['ok']}  ({len(report['findings'])} findings)")
    for f in report["findings"]:
        print(f"      [{f['kind']}] {f['detail']}")

    print("5) Asking a question (LLM cascade -> offline fallback):")
    answer = service.ask("How long do I have to report a personal data breach?")
    print(f"   A ({answer['source']}): {answer['answer']}")
    print(f"   cited: {answer['cited_norms']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="NormaGraph CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("demo", help="build the graph and run searches, impact and integrity")
    args = parser.parse_args()
    if args.command == "demo":
        demo()


if __name__ == "__main__":
    main()
