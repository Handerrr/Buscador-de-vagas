"""Testes das configurações da aplicação."""

import pytest

from job_monitor import load_database_settings


def test_load_database_settings_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Carrega todos os dados de conexão das variáveis de ambiente."""
    monkeypatch.setenv("DB_HOST", "database.local")
    monkeypatch.setenv("DB_PORT", "5433")
    monkeypatch.setenv("DB_NAME", "job_monitor_test")
    monkeypatch.setenv("DB_USER", "test_user")
    monkeypatch.setenv("DB_PASSWORD", "test_password")

    settings = load_database_settings(load_env_file=False)

    assert settings.host == "database.local"
    assert settings.port == 5433
    assert settings.name == "job_monitor_test"
    assert settings.user == "test_user"
    assert settings.password == "test_password"


def test_missing_required_settings_report_variables(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Informa quais configurações obrigatórias não foram definidas."""
    for variable in ("DB_NAME", "DB_USER", "DB_PASSWORD"):
        monkeypatch.delenv(variable, raising=False)

    with pytest.raises(ValueError) as captured_error:
        load_database_settings(load_env_file=False)

    assert str(captured_error.value) == (
        "Variáveis de ambiente obrigatórias ausentes: "
        "DB_NAME, DB_USER, DB_PASSWORD"
    )


def test_invalid_database_port_reports_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Rejeita uma porta que não possa ser convertida para número inteiro."""
    monkeypatch.setenv("DB_PORT", "invalid")
    monkeypatch.setenv("DB_NAME", "job_monitor_test")
    monkeypatch.setenv("DB_USER", "test_user")
    monkeypatch.setenv("DB_PASSWORD", "test_password")

    with pytest.raises(ValueError, match="DB_PORT deve ser um número inteiro"):
        load_database_settings(load_env_file=False)

