from __future__ import annotations

from normagraph import cli


def test_demo_runs(capsys):
    cli.demo()
    out = capsys.readouterr().out
    assert "norm graph" in out
    assert "Impact of changing ART-2" in out
    assert "dangling_reference" in out


def test_main_dispatches_demo(monkeypatch):
    called = {"demo": False}
    monkeypatch.setattr(cli, "demo", lambda: called.__setitem__("demo", True))
    monkeypatch.setattr("sys.argv", ["normagraph", "demo"])
    cli.main()
    assert called["demo"] is True
