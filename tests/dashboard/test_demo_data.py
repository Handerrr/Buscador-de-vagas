"""Testes dos exemplos exclusivos do modo demonstração."""

from datetime import UTC, datetime

import pytest

from job_monitor.dashboard.demo_data import create_demo_rows, is_demo_mode_enabled


def test_demo_mode_is_disabled_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    """Evita acrescentar exemplos sem configuração explícita."""
    monkeypatch.delenv("DASHBOARD_DEMO_MODE", raising=False)

    assert is_demo_mode_enabled() is False


def test_demo_mode_accepts_true_value(monkeypatch: pytest.MonkeyPatch) -> None:
    """Reconhece a opção usada pelo ambiente Docker."""
    monkeypatch.setenv("DASHBOARD_DEMO_MODE", "true")

    assert is_demo_mode_enabled() is True


def test_demo_rows_are_clearly_identified_and_have_no_application_link() -> None:
    """Impede que exemplos sejam confundidos com oportunidades reais."""
    reference_time = datetime(2026, 8, 25, tzinfo=UTC)

    rows = create_demo_rows(reference_time=reference_time)

    assert len(rows) == 12
    assert all(row["Fonte"] == "Demonstração" for row in rows)
    assert all(row["Link"] is None for row in rows)
    assert all("Exemplo fictício" in row["Descrição"] for row in rows)
