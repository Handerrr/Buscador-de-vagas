"""Testes das notificações enviadas pelo Telegram."""

import json
from io import BytesIO
from typing import Any

import pytest

from job_monitor import Job, ScoredJob, TelegramSettings
from job_monitor.notifier import (
    TelegramNotificationError,
    format_job_notification,
    send_job_notification,
    send_telegram_message,
)
from job_monitor.notifier import telegram


class FakeResponse(BytesIO):
    """Simula uma resposta JSON da API do Telegram."""


def _create_scored_job() -> ScoredJob:
    """Cria uma vaga classificada para os testes."""
    job = Job(
        title="Data Analyst",
        company="Empresa Exemplo",
        url="https://remoteok.com/remote-jobs/123",
        source="Remote OK",
        location="Brazil",
    )
    return ScoredJob(
        job=job,
        score=4,
        matched_keywords=("Python", "SQL"),
    )


def test_format_job_notification_includes_relevant_information() -> None:
    """Inclui dados da vaga, pontuação, fonte e link na mensagem."""
    message = format_job_notification(_create_scored_job())

    assert "Cargo: Data Analyst" in message
    assert "Empresa: Empresa Exemplo" in message
    assert "Localização: Brazil" in message
    assert "Pontuação: 4" in message
    assert "Termos encontrados: Python, SQL" in message
    assert "Fonte: Remote OK" in message
    assert "Link: https://remoteok.com/remote-jobs/123" in message


def test_send_telegram_message_posts_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Envia a mensagem ao endpoint e chat configurados."""
    settings = TelegramSettings(bot_token="test-token", chat_id="123456")

    def fake_urlopen(request: Any, timeout: float) -> FakeResponse:
        assert request.full_url == (
            "https://api.telegram.org/bottest-token/sendMessage"
        )
        assert request.method == "POST"
        assert request.get_header("Content-type") == "application/json"
        assert timeout == 5.0
        assert json.loads(request.data) == {
            "chat_id": "123456",
            "text": "Mensagem de teste",
            "disable_web_page_preview": True,
        }
        return FakeResponse(b'{"ok": true, "result": {"message_id": 1}}')

    monkeypatch.setattr(telegram, "urlopen", fake_urlopen)

    send_telegram_message(settings, "Mensagem de teste", timeout=5.0)


def test_send_telegram_message_reports_refused_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Transforma uma recusa da API em erro específico do notifier."""
    settings = TelegramSettings(bot_token="test-token", chat_id="invalid")
    monkeypatch.setattr(
        telegram,
        "urlopen",
        lambda request, timeout: FakeResponse(b'{"ok": false}'),
    )

    with pytest.raises(TelegramNotificationError, match="recusou"):
        send_telegram_message(settings, "Mensagem")


def test_send_job_notification_uses_formatted_message(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Combina a formatação e o envio da notificação."""
    settings = TelegramSettings(bot_token="test-token", chat_id="123456")
    received_messages: list[str] = []
    monkeypatch.setattr(
        telegram,
        "send_telegram_message",
        lambda received_settings, message: received_messages.append(message),
    )

    send_job_notification(settings, _create_scored_job())

    assert len(received_messages) == 1
    assert received_messages[0].startswith("Nova vaga relevante!")

