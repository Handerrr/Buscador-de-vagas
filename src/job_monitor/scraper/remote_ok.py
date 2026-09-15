"""Coleta de vagas pela API pública do Remote OK."""

from datetime import UTC, datetime
from html import unescape
from urllib.parse import urlencode

from job_monitor.models import Job
from job_monitor.scraper.common import fetch_json, html_to_text


REMOTE_OK_API_URL = "https://remoteok.com/api"
REMOTE_OK_SOURCE = "Remote OK"
class RemoteOKError(RuntimeError):
    """Indica uma falha ao coletar ou interpretar vagas do Remote OK."""


def _build_api_url(tags: tuple[str, ...]) -> str:
    """Monta a URL da API com filtros opcionais de tags."""
    normalized_tags = [tag.strip() for tag in tags if tag.strip()]
    if not normalized_tags:
        return REMOTE_OK_API_URL

    query = urlencode({"tags": ",".join(normalized_tags)})
    return f"{REMOTE_OK_API_URL}?{query}"


def _parse_job(data: dict[str, object]) -> Job:
    """Converte uma vaga da API para o modelo interno do projeto."""
    location = str(data.get("location", "")).strip() or None
    description = html_to_text(str(data.get("description", "")))

    try:
        published_at = datetime.fromtimestamp(int(data["epoch"]), tz=UTC)
        title = unescape(str(data["position"]))
        company = unescape(str(data["company"]))
        url = str(data["url"])
    except (KeyError, TypeError, ValueError, OSError) as error:
        raise RemoteOKError("A API retornou uma vaga com dados inválidos.") from error

    return Job(
        title=title,
        company=company,
        url=url,
        source=REMOTE_OK_SOURCE,
        location=location,
        description=description,
        published_at=published_at,
    )


def fetch_remote_ok_jobs(
    *,
    tags: tuple[str, ...] = (),
    timeout: float = 15.0,
) -> list[Job]:
    """Busca vagas na API pública do Remote OK."""
    payload = fetch_json(
        _build_api_url(tags),
        timeout=timeout,
        error_type=RemoteOKError,
        error_message="Não foi possível obter vagas do Remote OK.",
    )

    if not isinstance(payload, list):
        raise RemoteOKError("A API do Remote OK retornou um formato inesperado.")

    job_items = [
        item
        for item in payload
        if isinstance(item, dict) and item.get("id") is not None
    ]
    return [_parse_job(item) for item in job_items]
