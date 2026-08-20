"""Coleta de vagas pela API pública do Remote OK."""

import json
from datetime import UTC, datetime
from html import unescape
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from job_monitor.models import Job


REMOTE_OK_API_URL = "https://remoteok.com/api"
REMOTE_OK_SOURCE = "Remote OK"
USER_AGENT = "JobMonitorPortfolio/0.1"


class RemoteOKError(RuntimeError):
    """Indica uma falha ao coletar ou interpretar vagas do Remote OK."""


class _HTMLTextExtractor(HTMLParser):
    """Extrai somente o conteúdo textual de uma descrição HTML."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)

    def get_text(self) -> str:
        return " ".join(" ".join(self.parts).split())


def _html_to_text(value: str) -> str | None:
    """Converte HTML em texto simples e retorna ``None`` se ficar vazio."""
    extractor = _HTMLTextExtractor()
    extractor.feed(value)
    text = extractor.get_text()
    return text or None


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
    description = _html_to_text(str(data.get("description", "")))

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
    request = Request(
        _build_api_url(tags),
        headers={
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        },
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise RemoteOKError("Não foi possível obter vagas do Remote OK.") from error

    if not isinstance(payload, list):
        raise RemoteOKError("A API do Remote OK retornou um formato inesperado.")

    job_items = [
        item
        for item in payload
        if isinstance(item, dict) and item.get("id") is not None
    ]
    return [_parse_job(item) for item in job_items]

