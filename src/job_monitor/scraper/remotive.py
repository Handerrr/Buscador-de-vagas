"""Coleta de vagas pela API pública da Remotive."""

import json
import re
from datetime import datetime
from html import unescape
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from job_monitor.models import Job


REMOTIVE_API_URL = "https://remotive.com/api/remote-jobs"
REMOTIVE_SOURCE = "Remotive"
USER_AGENT = "JobMonitorPortfolio/0.1"


class RemotiveError(RuntimeError):
    """Indica uma falha ao coletar ou interpretar vagas da Remotive."""


class _HTMLTextExtractor(HTMLParser):
    """Extrai texto simples das descrições HTML retornadas pela API."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def get_text(self) -> str:
        text = " ".join(" ".join(self.parts).split())
        return re.sub(r"\s+([.,;:!?])", r"\1", text)


def _html_to_text(value: str) -> str | None:
    extractor = _HTMLTextExtractor()
    extractor.feed(value)
    return extractor.get_text() or None


def _parse_publication_date(value: object) -> datetime:
    text = str(value).strip().replace("Z", "+00:00")
    parsed_date = datetime.fromisoformat(text)
    if parsed_date.tzinfo is None:
        parsed_date = parsed_date.astimezone()
    return parsed_date


def _parse_job(data: dict[str, object]) -> Job:
    try:
        title = unescape(str(data["title"]))
        company = unescape(str(data["company_name"]))
        url = str(data["url"])
        published_at = _parse_publication_date(data["publication_date"])
    except (KeyError, TypeError, ValueError) as error:
        raise RemotiveError("A API retornou uma vaga com dados inválidos.") from error

    location = str(data.get("candidate_required_location", "")).strip() or None
    description = _html_to_text(str(data.get("description", "")))
    return Job(
        title=title,
        company=company,
        url=url,
        source=REMOTIVE_SOURCE,
        location=location,
        description=description,
        published_at=published_at,
    )


def fetch_remotive_jobs(*, timeout: float = 15.0) -> list[Job]:
    """Busca todas as vagas disponíveis na API pública da Remotive."""
    request = Request(
        REMOTIVE_API_URL,
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise RemotiveError("Não foi possível obter vagas da Remotive.") from error

    if not isinstance(payload, dict) or not isinstance(payload.get("jobs"), list):
        raise RemotiveError("A API da Remotive retornou um formato inesperado.")

    job_items = [item for item in payload["jobs"] if isinstance(item, dict)]
    return [_parse_job(item) for item in job_items]
