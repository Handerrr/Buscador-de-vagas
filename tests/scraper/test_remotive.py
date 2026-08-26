"""Testes do coletor da API pública da Remotive."""

import json
from datetime import datetime
from io import BytesIO
from typing import Any
from urllib.error import URLError

import pytest

from job_monitor.scraper import RemotiveError, fetch_remotive_jobs
from job_monitor.scraper import remotive


class FakeResponse(BytesIO):
    """Simula uma resposta HTTP contendo JSON."""


def test_fetch_remotive_jobs_maps_api_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = {
        "job-count": 1,
        "jobs": [
            {
                "id": 123,
                "url": "https://remotive.com/remote-jobs/software-dev/123",
                "title": "Python &amp; Data Engineer",
                "company_name": "Data &amp; Co",
                "publication_date": "2026-08-25T12:30:00+00:00",
                "candidate_required_location": "Americas",
                "description": "<p>Build <strong>pipelines</strong>.</p>",
            }
        ],
    }

    def fake_urlopen(request: Any, timeout: float) -> FakeResponse:
        assert request.full_url == "https://remotive.com/api/remote-jobs"
        assert request.get_header("Accept") == "application/json"
        assert request.get_header("User-agent") == "JobMonitorPortfolio/0.1"
        assert timeout == 5.0
        return FakeResponse(json.dumps(payload).encode("utf-8"))

    monkeypatch.setattr(remotive, "urlopen", fake_urlopen)
    jobs = fetch_remotive_jobs(timeout=5.0)

    assert len(jobs) == 1
    assert jobs[0].title == "Python & Data Engineer"
    assert jobs[0].company == "Data & Co"
    assert jobs[0].source == "Remotive"
    assert jobs[0].location == "Americas"
    assert jobs[0].description == "Build pipelines."
    assert jobs[0].published_at == datetime.fromisoformat(
        "2026-08-25T12:30:00+00:00"
    )


def test_fetch_remotive_jobs_rejects_unexpected_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        remotive,
        "urlopen",
        lambda request, timeout: FakeResponse(b'{"error": "unexpected"}'),
    )

    with pytest.raises(RemotiveError, match="formato inesperado"):
        fetch_remotive_jobs()


def test_fetch_remotive_jobs_reports_network_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_request(request: Any, timeout: float) -> FakeResponse:
        raise URLError("offline")

    monkeypatch.setattr(remotive, "urlopen", fail_request)

    with pytest.raises(RemotiveError, match="Não foi possível"):
        fetch_remotive_jobs()
