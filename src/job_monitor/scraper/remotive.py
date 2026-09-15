"""Coleta de vagas pela API pública da Remotive."""

from datetime import datetime
from html import unescape

from job_monitor.models import Job
from job_monitor.scraper.common import fetch_json, html_to_text


REMOTIVE_API_URL = "https://remotive.com/api/remote-jobs"
REMOTIVE_SOURCE = "Remotive"
class RemotiveError(RuntimeError):
    """Indica uma falha ao coletar ou interpretar vagas da Remotive."""


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
    description = html_to_text(str(data.get("description", "")))
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
    payload = fetch_json(
        REMOTIVE_API_URL,
        timeout=timeout,
        error_type=RemotiveError,
        error_message="Não foi possível obter vagas da Remotive.",
    )

    if not isinstance(payload, dict) or not isinstance(payload.get("jobs"), list):
        raise RemotiveError("A API da Remotive retornou um formato inesperado.")

    job_items = [item for item in payload["jobs"] if isinstance(item, dict)]
    return [_parse_job(item) for item in job_items]
