"""Testes do fluxo de processamento das vagas."""

from types import TracebackType
from typing import Any

from job_monitor import Job, JobProcessingStatus, process_job


class FakeTransaction:
    """Simula uma transação controlada pelo serviço."""

    def __enter__(self) -> None:
        return None

    def __exit__(
        self,
        exception_type: type[BaseException] | None,
        exception: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None


class FakeCursor:
    """Simula o resultado de uma tentativa de inserção."""

    def __init__(self, returned_row: tuple[int] | None) -> None:
        self.returned_row = returned_row

    def fetchone(self) -> tuple[int] | None:
        return self.returned_row


class FakeConnection:
    """Registra se o serviço abriu transação e executou SQL."""

    def __init__(self, returned_row: tuple[int] | None) -> None:
        self.returned_row = returned_row
        self.transaction_count = 0
        self.execute_count = 0
        self.executed_parameters: tuple[Any, ...] | None = None

    def transaction(self) -> FakeTransaction:
        self.transaction_count += 1
        return FakeTransaction()

    def execute(
        self,
        command: str,
        parameters: tuple[Any, ...],
    ) -> FakeCursor:
        self.execute_count += 1
        self.executed_parameters = parameters
        return FakeCursor(self.returned_row)


def _create_job() -> Job:
    """Cria uma vaga válida com espaços para exercitar a normalização."""
    return Job(
        title="  Pessoa   Desenvolvedora Python  ",
        company="  Empresa Exemplo ",
        url="  https://example.com/jobs/123  ",
        source="  Fonte Exemplo ",
    )


def test_process_job_normalizes_and_inserts_valid_job() -> None:
    """Normaliza uma vaga válida e informa que ela foi inserida."""
    connection = FakeConnection(returned_row=(1,))

    result = process_job(connection, _create_job())

    assert result.status is JobProcessingStatus.INSERTED
    assert result.job.title == "Pessoa Desenvolvedora Python"
    assert result.job.url == "https://example.com/jobs/123"
    assert result.errors == ()
    assert connection.transaction_count == 1
    assert connection.execute_count == 1


def test_process_job_reports_duplicate() -> None:
    """Informa quando uma vaga válida já está armazenada."""
    connection = FakeConnection(returned_row=None)

    result = process_job(connection, _create_job())

    assert result.status is JobProcessingStatus.DUPLICATE
    assert result.errors == ()
    assert connection.transaction_count == 1
    assert connection.execute_count == 1


def test_process_job_does_not_store_invalid_job() -> None:
    """Retorna os erros sem abrir transação ou executar SQL."""
    connection = FakeConnection(returned_row=(1,))
    invalid_job = Job(
        title="   ",
        company="Empresa Exemplo",
        url="invalid-url",
        source="Fonte Exemplo",
    )

    result = process_job(connection, invalid_job)

    assert result.status is JobProcessingStatus.INVALID
    assert result.errors == (
        "O título da vaga é obrigatório.",
        "A URL da vaga deve usar HTTP ou HTTPS e possuir um domínio.",
    )
    assert connection.transaction_count == 0
    assert connection.execute_count == 0

