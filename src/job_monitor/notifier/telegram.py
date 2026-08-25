"""Envio de notificações pela API oficial do Telegram."""

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from job_monitor.config import TelegramSettings
from job_monitor.scoring import ScoredJob


TELEGRAM_API_BASE_URL = "https://api.telegram.org"


class TelegramNotificationError(RuntimeError):
    """Indica uma falha ao enviar uma mensagem pelo Telegram."""


def format_job_notification(scored_job: ScoredJob) -> str:
    """Formata uma vaga classificada como uma mensagem legível."""
    job = scored_job.job
    location = job.location or "Não informada"
    matched_keywords = ", ".join(scored_job.matched_keywords) or "Nenhuma"
    return "\n".join(
        (
            "Nova vaga relevante!",
            "",
            f"Cargo: {job.title}",
            f"Empresa: {job.company}",
            f"Localização: {location}",
            f"Pontuação: {scored_job.score}",
            f"Termos encontrados: {matched_keywords}",
            f"Fonte: {job.source}",
            f"Link: {job.url}",
        )
    )


def send_telegram_message(
    settings: TelegramSettings,
    message: str,
    *,
    timeout: float = 15.0,
) -> None:
    """Envia uma mensagem de texto para o chat configurado."""
    endpoint = f"{TELEGRAM_API_BASE_URL}/bot{settings.bot_token}/sendMessage"
    body = json.dumps(
        {
            "chat_id": settings.chat_id,
            "text": message,
            "disable_web_page_preview": True,
        }
    ).encode("utf-8")
    request = Request(
        endpoint,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=timeout) as response:
            result = json.load(response)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError):
        raise TelegramNotificationError(
            "Não foi possível enviar a notificação pelo Telegram."
        ) from None

    if not isinstance(result, dict) or result.get("ok") is not True:
        raise TelegramNotificationError(
            "O Telegram recusou o envio da notificação."
        )


def send_job_notification(
    settings: TelegramSettings,
    scored_job: ScoredJob,
) -> None:
    """Formata e envia uma notificação de nova vaga."""
    send_telegram_message(settings, format_job_notification(scored_job))
