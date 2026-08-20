"""Testes das operações de armazenamento de vagas."""

from datetime import UTC, datetime
from typing import Any

from job_monitor import Job, generate_job_key
from job_monitor.database.repository import INSERT_JOB, save_job


class FakeCursor:
    """Simula o resultado retornado pelo PostgreSQL."""

    def __init__(self, returned_row: tuple[int] | None) -> None:
        self.returned_row = returned_row

    def fetchone(self) -> tuple[int] | None:
        return self.returned_row


class FakeConnection:
    """Registra o comando e os parâmetros recebidos no teste."""

    def __init__(self, returned_row: tuple[int] | None) -> None:
        self.returned_row = returned_row
        self.executed_command: str | None = None
        self.executed_parameters: tuple[Any, ...] | None = None

    def execute(
        self,
        command: str,
        parameters: tuple[Any, ...],
    ) -> FakeCursor:
        self.executed_command = command
        self.executed_parameters = parameters
        return FakeCursor(self.returned_row)


def _create_job() -> Job:
    """Cria uma vaga completa para os testes do repositório."""
    return Job(
        title="Pessoa Desenvolvedora Python",
        company="Empresa Exemplo",
        url="https://example.com/jobs/123",
        source="Fonte Exemplo",
        location="São Paulo, SP",
        description="Desenvolvimento de aplicações em Python.",
        published_at=datetime(2026, 8, 20, 9, 0, tzinfo=UTC),
        collected_at=datetime(2026, 8, 20, 10, 0, tzinfo=UTC),
    )


def test_save_job_inserts_all_job_fields() -> None:
    """Envia ao PostgreSQL a chave e todos os dados da vaga."""
    connection = FakeConnection(returned_row=(1,))
    job = _create_job()

    was_inserted = save_job(connection, job)

    assert was_inserted is True
    assert connection.executed_command == INSERT_JOB
    assert connection.executed_parameters == (
        generate_job_key(job),
        job.title,
        job.company,
        job.url,
        job.source,
        job.location,
        job.description,
        job.published_at,
        job.collected_at,
    )


def test_save_job_returns_false_for_duplicate() -> None:
    """Informa quando a restrição única ignora uma vaga duplicada."""
    connection = FakeConnection(returned_row=None)

    was_inserted = save_job(connection, _create_job())

    assert was_inserted is False


def test_insert_uses_database_conflict_protection() -> None:
    """Mantém no SQL a proteção contra conflito da chave da vaga."""
    normalized_sql = " ".join(INSERT_JOB.split())

    assert "ON CONFLICT (job_key) DO NOTHING" in normalized_sql
    assert normalized_sql.endswith("RETURNING id;")

