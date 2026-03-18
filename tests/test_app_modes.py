from __future__ import annotations

import app


class FakeStreamlit:
    def __init__(self):
        self.messages: list[str] = []

    def info(self, message: str) -> None:
        self.messages.append(message)


def test_mode_indicator_google(monkeypatch):
    fake_st = FakeStreamlit()
    monkeypatch.setattr(app, "st", fake_st)

    app.render_mode_indicator("google-authenticated")

    assert fake_st.messages == ["Scoring mode: Google-authenticated"]


def test_mode_indicator_local(monkeypatch):
    fake_st = FakeStreamlit()
    monkeypatch.setattr(app, "st", fake_st)

    app.render_mode_indicator("local-csv-fallback")

    assert fake_st.messages == ["Scoring mode: Local CSV fallback"]
