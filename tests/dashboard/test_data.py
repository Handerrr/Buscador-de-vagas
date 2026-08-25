"""Testes da preparação dos dados usados pelo painel."""

from datetime import UTC, datetime
from typing import Any

from job_monitor.dashboard import data
from job_monitor.models import Job


class FakeConnection:
    """Conexão mínima que permite conferir seu encerramento."""

    def __init__(self) -> None:
        self.was_closed = False

    def close(self) -> None:
        self.was_closed = True


def test_job_to_dashboard_row_uses_friendly_labels() -> None:
    """Prepara os campos que serão apresentados ao visitante."""
    collected_at = datetime(2026, 8, 25, tzinfo=UTC)
    job = Job(
        title="Pessoa Desenvolvedora Python",
        company="Empresa Exemplo",
        url="https://example.com/job",
        source="Remote OK",
        collected_at=collected_at,
    )

    assert data.job_to_dashboard_row(job) == {
        "Cargo": "Pessoa Desenvolvedora Python",
        "Empresa": "Empresa Exemplo",
        "Localização": "Não informada",
        "Fonte": "Remote OK",
        "Publicada em": None,
        "Coletada em": collected_at,
        "Link": "https://example.com/job",
        "Descrição": "Descrição não informada.",
    }


def test_load_dashboard_rows_closes_database_connection(monkeypatch: Any) -> None:
    """Libera a conexão depois de carregar as vagas."""
    connection = FakeConnection()
    job = Job(
        title="Data Analyst",
        company="Empresa Exemplo",
        url="https://example.com/job",
        source="Remote OK",
    )
    monkeypatch.setattr(data, "load_database_settings", lambda: object())
    monkeypatch.setattr(data, "connect_database", lambda settings: connection)
    monkeypatch.setattr(data, "initialize_database", lambda received: None)
    monkeypatch.setattr(data, "list_jobs", lambda received, limit: [job])

    rows = data.load_dashboard_rows(limit=10)

    assert rows[0]["Cargo"] == "Data Analyst"
    assert connection.was_closed is True


def test_filter_dashboard_rows_searches_title_and_company() -> None:
    """Permite pesquisar tanto pelo cargo quanto pela empresa."""
    rows = [
        {"Cargo": "Data Analyst", "Empresa": "Acme", "Fonte": "A", "Localização": "Brasil"},
        {"Cargo": "Python Developer", "Empresa": "Beta", "Fonte": "B", "Localização": "Brazil"},
    ]

    assert data.filter_dashboard_rows(rows, search="acme") == [rows[0]]
    assert data.filter_dashboard_rows(rows, search="python") == [rows[1]]


def test_summarize_and_group_dashboard_rows() -> None:
    """Calcula indicadores e agrupamentos usados nos gráficos."""
    first_date = datetime(2026, 8, 24, tzinfo=UTC)
    last_date = datetime(2026, 8, 25, tzinfo=UTC)
    rows = [
        {"Empresa": "Acme", "Fonte": "Remote OK", "Coletada em": first_date},
        {"Empresa": "Acme", "Fonte": "Remote OK", "Coletada em": last_date},
        {"Empresa": "Beta", "Fonte": "Outra", "Coletada em": last_date},
    ]

    summary = data.summarize_dashboard_rows(rows)

    assert summary.total_jobs == 3
    assert summary.total_companies == 2
    assert summary.total_sources == 2
    assert summary.latest_collection == last_date
    assert data.count_rows_by_field(rows, "Empresa") == {"Acme": 2, "Beta": 1}
