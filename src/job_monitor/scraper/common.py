"""Utilitários compartilhados pelos coletores de vagas."""

import json
import re
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


USER_AGENT = "JobMonitorPortfolio/0.1"


class _HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def html_to_text(value: str) -> str | None:
    """Converte HTML em texto simples, normalizando espaços e pontuação."""
    extractor = _HTMLTextExtractor()
    extractor.feed(value)
    text = " ".join(" ".join(extractor.parts).split())
    return re.sub(r"\s+([.,;:!?])", r"\1", text) or None


def fetch_json(
    url: str,
    *,
    timeout: float,
    error_type: type[RuntimeError],
    error_message: str,
) -> object:
    """Executa um GET padronizado e converte a resposta JSON."""
    request = Request(
        url,
        headers={"Accept": "application/json", "User-Agent": USER_AGENT},
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return json.load(response)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise error_type(error_message) from error
