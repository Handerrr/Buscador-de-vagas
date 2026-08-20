"""Testes da inicialização das tabelas do PostgreSQL."""

from types import TracebackType
from typing import Any

from job_monitor.database.schema import CREATE_JOBS_TABLE, initialize_database


class FakeTransaction:
    """Contexto de transação usado sem acessar um banco real."""

    def __enter__(self) -> None:
        return None

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None


class FakeConnection:
    """Registra os comandos SQL recebidos durante o teste."""

    def __init__(self) -> None:
        self.executed_commands: list[str] = []

    def transaction(self) -> FakeTransaction:
        return FakeTransaction()

    def execute(self, command: str) -> None:
        self.executed_commands.append(command)


def test_initialize_database_executes_jobs_table_creation() -> None:
    """Executa a criação da tabela dentro de uma transação."""
    connection: Any = FakeConnection()

    initialize_database(connection)

    assert connection.executed_commands == [CREATE_JOBS_TABLE]


def test_jobs_table_has_unique_job_key() -> None:
    """Mantém a chave de duplicidade obrigatória e única."""
    normalized_sql = " ".join(CREATE_JOBS_TABLE.split())

    assert "job_key VARCHAR(64) NOT NULL UNIQUE" in normalized_sql

