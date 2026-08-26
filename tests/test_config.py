"""Testes das configurações da aplicação."""

import pytest

from job_monitor import (
    JobLevel,
    TelegramSettings,
    load_database_settings,
    load_job_filter_criteria,
    load_job_scoring_keywords,
    load_telegram_settings,
)


def test_load_database_settings_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Carrega todos os dados de conexão das variáveis de ambiente."""
    monkeypatch.setenv("DB_HOST", "database.local")
    monkeypatch.setenv("DB_PORT", "5433")
    monkeypatch.setenv("DB_NAME", "job_monitor_test")
    monkeypatch.setenv("DB_USER", "test_user")
    monkeypatch.setenv("DB_PASSWORD", "test_password")
    monkeypatch.delenv("DATABASE_URL", raising=False)

    settings = load_database_settings(load_env_file=False)

    assert settings.host == "database.local"
    assert settings.port == 5433
    assert settings.name == "job_monitor_test"
    assert settings.user == "test_user"
    assert settings.password == "test_password"
    assert settings.connection_url is None


def test_database_url_has_priority_over_individual_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Usa a conexão única fornecida por bancos PostgreSQL gerenciados."""
    connection_url = (
        "postgresql://cloud_user:cloud_password@db.example.com:5433/portfolio"
        "?sslmode=require"
    )
    monkeypatch.setenv("DATABASE_URL", connection_url)

    settings = load_database_settings(load_env_file=False)

    assert settings.host == "db.example.com"
    assert settings.port == 5433
    assert settings.name == "portfolio"
    assert settings.connection_url == connection_url


@pytest.mark.parametrize(
    "connection_url",
    [
        "https://db.example.com/portfolio",
        "postgresql:///portfolio",
        "postgresql://db.example.com",
        "postgresql://db.example.com:invalid/portfolio",
        "postgresql://user:password@db.example.com/portfolio",
    ],
)
def test_invalid_database_url_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
    connection_url: str,
) -> None:
    """Rejeita URLs incompletas sem incluir seu conteúdo no erro."""
    monkeypatch.setenv("DATABASE_URL", connection_url)

    with pytest.raises(ValueError) as captured_error:
        load_database_settings(load_env_file=False)

    assert connection_url not in str(captured_error.value)


def test_missing_required_settings_report_variables(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Informa quais configurações obrigatórias não foram definidas."""
    for variable in ("DB_NAME", "DB_USER", "DB_PASSWORD"):
        monkeypatch.delenv(variable, raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)

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
    monkeypatch.delenv("DATABASE_URL", raising=False)

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


def test_load_job_scoring_keywords_from_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Carrega os termos de pontuação preservando sua ordem."""
    monkeypatch.setenv("JOB_PREFERRED_KEYWORDS", "Python, SQL, Power BI")

    assert load_job_scoring_keywords(load_env_file=False) == (
        "Python",
        "SQL",
        "Power BI",
    )


def test_load_telegram_settings_from_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Carrega token e chat sem expor seus valores em mensagens."""
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "123456")

    assert load_telegram_settings(load_env_file=False) == TelegramSettings(
        bot_token="test-token",
        chat_id="123456",
    )
