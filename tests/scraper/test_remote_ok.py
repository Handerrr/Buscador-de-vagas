"""Testes do coletor da API do Remote OK."""

import json
from datetime import UTC, datetime
from io import BytesIO
from typing import Any

import pytest

from job_monitor.scraper import RemoteOKError, fetch_remote_ok_jobs
from job_monitor.scraper import remote_ok


class FakeResponse(BytesIO):
    """Simula uma resposta HTTP contendo JSON."""


def test_fetch_remote_ok_jobs_maps_api_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ignora metadados e converte a vaga para o modelo interno."""
    payload = [
        {"last_updated": 1_777_000_000, "legal": "Credit Remote OK"},
        {
            "id": "123",
            "epoch": 1_777_003_200,
            "company": "Data &amp; Co",
            "position": "Python &amp; Data Engineer",
            "description": "<p>Build <strong>data</strong> pipelines.</p>",
            "location": "  Worldwide  ",
            "url": "https://remoteok.com/remote-jobs/123",
            "tags": ["python", "data"],
        },
    ]

    def fake_urlopen(request: Any, timeout: float) -> FakeResponse:
        assert request.full_url == "https://remoteok.com/api?tags=python%2Cdata"
        assert request.get_header("Accept") == "application/json"
        assert request.get_header("User-agent") == "JobMonitorPortfolio/0.1"
        assert timeout == 5.0
        return FakeResponse(json.dumps(payload).encode("utf-8"))

    monkeypatch.setattr(remote_ok, "urlopen", fake_urlopen)

    jobs = fetch_remote_ok_jobs(tags=("python", "data"), timeout=5.0)

    assert len(jobs) == 1
    assert jobs[0].title == "Python & Data Engineer"
    assert jobs[0].company == "Data & Co"
    assert jobs[0].url == "https://remoteok.com/remote-jobs/123"
    assert jobs[0].source == "Remote OK"
    assert jobs[0].location == "Worldwide"
    assert jobs[0].description == "Build data pipelines."
    assert jobs[0].published_at == datetime.fromtimestamp(1_777_003_200, tz=UTC)


def test_fetch_remote_ok_jobs_without_tags_uses_base_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Não adiciona query string quando filtros não são informados."""
    def fake_urlopen(request: Any, timeout: float) -> FakeResponse:
        assert request.full_url == "https://remoteok.com/api"
        return FakeResponse(b"[]")

    monkeypatch.setattr(remote_ok, "urlopen", fake_urlopen)

    assert fetch_remote_ok_jobs() == []


def test_fetch_remote_ok_jobs_rejects_unexpected_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Informa claramente quando a resposta não é uma lista."""
    def fake_urlopen(request: Any, timeout: float) -> FakeResponse:
        return FakeResponse(b'{"error": "unexpected"}')

    monkeypatch.setattr(remote_ok, "urlopen", fake_urlopen)

    with pytest.raises(RemoteOKError, match="formato inesperado"):
        fetch_remote_ok_jobs()

