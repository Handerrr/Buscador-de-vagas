"""Testes das configurações da aplicação."""

import pytest

from job_monitor import JobLevel, load_database_settings, load_job_filter_criteria


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


def test_load_job_filter_criteria_from_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Converte listas do ambiente em critérios estruturados."""
    monkeypatch.setenv("JOB_TITLES", "Analista de Dados, Data Analyst")
    monkeypatch.setenv("JOB_INCLUDED_KEYWORDS", "Python, SQL")
    monkeypatch.setenv("JOB_EXCLUDED_KEYWORDS", "manager, director")
    monkeypatch.setenv("JOB_LOCATIONS", "Brasil, Brazil")
    monkeypatch.setenv("JOB_LEVELS", "estágio, junior, pleno, senior")

    criteria = load_job_filter_criteria(load_env_file=False)

    assert criteria.title_keywords == ("Analista de Dados", "Data Analyst")
    assert criteria.included_keywords == ("Python", "SQL")
    assert criteria.excluded_keywords == ("manager", "director")
    assert criteria.locations == ("Brasil", "Brazil")
    assert criteria.levels == (
        JobLevel.INTERNSHIP,
        JobLevel.JUNIOR,
        JobLevel.MID_LEVEL,
        JobLevel.SENIOR,
    )
