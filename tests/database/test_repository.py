"""Testes das operações de armazenamento de vagas."""

from datetime import UTC, datetime
from typing import Any

from job_monitor import Job, generate_job_key
from job_monitor.database.repository import (
    INSERT_JOB,
    LIST_JOBS,
    SELECT_JOB_BY_KEY,
    find_job_by_key,
    list_jobs,
    save_job,
)


class FakeCursor:
    """Simula o resultado retornado pelo PostgreSQL."""

    def __init__(
        self,
        returned_row: tuple[Any, ...] | None,
        returned_rows: list[tuple[Any, ...]],
    ) -> None:
        self.returned_row = returned_row
        self.returned_rows = returned_rows

    def fetchone(self) -> tuple[Any, ...] | None:
        return self.returned_row

    def fetchall(self) -> list[tuple[Any, ...]]:
        return self.returned_rows


class FakeConnection:
    """Registra o comando e os parâmetros recebidos no teste."""

    def __init__(
        self,
        returned_row: tuple[Any, ...] | None = None,
        returned_rows: list[tuple[Any, ...]] | None = None,
    ) -> None:
        self.returned_row = returned_row
        self.returned_rows = returned_rows or []
        self.executed_command: str | None = None
        self.executed_parameters: tuple[Any, ...] | None = None

    def execute(
        self,
        command: str,
        parameters: tuple[Any, ...],
    ) -> FakeCursor:
        self.executed_command = command
        self.executed_parameters = parameters
        return FakeCursor(self.returned_row, self.returned_rows)


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


def test_find_job_by_key_returns_job() -> None:
    """Converte a linha encontrada novamente para o modelo de vaga."""
    expected_job = _create_job()
    returned_row = (
        expected_job.title,
        expected_job.company,
        expected_job.url,
        expected_job.source,
        expected_job.location,
        expected_job.description,
        expected_job.published_at,
        expected_job.collected_at,
    )
    connection = FakeConnection(returned_row=returned_row)
    job_key = generate_job_key(expected_job)

    found_job = find_job_by_key(connection, job_key)

    assert found_job == expected_job
    assert connection.executed_command == SELECT_JOB_BY_KEY
    assert connection.executed_parameters == (job_key,)


def test_find_job_by_key_returns_none_when_not_found() -> None:
    """Retorna ``None`` quando não existe vaga com a chave informada."""
    connection = FakeConnection(returned_row=None)

    assert find_job_by_key(connection, "missing-key") is None


def test_list_jobs_returns_converted_rows() -> None:
    """Converte todas as linhas retornadas em objetos de vaga."""
    expected_job = _create_job()
    returned_row = (
        expected_job.title,
        expected_job.company,
        expected_job.url,
        expected_job.source,
        expected_job.location,
        expected_job.description,
        expected_job.published_at,
        expected_job.collected_at,
    )
    connection = FakeConnection(returned_rows=[returned_row])

    jobs = list_jobs(connection, limit=25)

    assert jobs == [expected_job]
    assert connection.executed_command == LIST_JOBS
    assert connection.executed_parameters == (25,)


def test_list_jobs_rejects_non_positive_limit() -> None:
    """Impede consultas com limite zero ou negativo."""
    connection = FakeConnection()

    for invalid_limit in (0, -1):
        try:
            list_jobs(connection, limit=invalid_limit)
        except ValueError as error:
            assert str(error) == "O limite deve ser maior que zero."
        else:
            raise AssertionError("Era esperado um ValueError para limite inválido.")
