"""Testes da coordenação principal do monitor."""

from typing import Any

import pytest

from job_monitor import Job
from job_monitor.config import TelegramSettings
from job_monitor.filtering import JobFilterCriteria
from job_monitor.main import MonitorSummary, run_monitor
from job_monitor.notifier import TelegramNotificationError
from job_monitor.service import JobProcessingResult, JobProcessingStatus
import job_monitor.main as main_module


class FakeConnection:
    """Simula uma conexão que registra seu fechamento."""

    def __init__(self) -> None:
        self.was_closed = False

    def close(self) -> None:
        self.was_closed = True


def _create_job(identifier: int) -> Job:
    """Cria uma vaga válida identificável para os testes."""
    return Job(
        title=f"Vaga {identifier}",
        company="Empresa Exemplo",
        url=f"https://example.com/jobs/{identifier}",
        source="Remote OK",
    )


def test_run_monitor_collects_processes_and_counts_results(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Coordena os componentes e contabiliza cada resultado."""
    jobs = [_create_job(identifier) for identifier in range(4)]
    statuses = iter(
        [
            JobProcessingStatus.INSERTED,
            JobProcessingStatus.DUPLICATE,
            JobProcessingStatus.INVALID,
        ]
    )
    connection = FakeConnection()
    initialized_connections: list[Any] = []
    processed_jobs: list[Job] = []
    notified_jobs: list[Job] = []

    monkeypatch.setattr(
        main_module,
        "fetch_remote_ok_jobs",
        lambda *, tags: jobs,
    )
    monkeypatch.setattr(main_module, "fetch_remotive_jobs", lambda: [])
    monkeypatch.setattr(main_module, "load_database_settings", lambda: object())
    monkeypatch.setattr(
        main_module,
        "connect_database",
        lambda settings: connection,
    )
    monkeypatch.setattr(
        main_module,
        "initialize_database",
        lambda received_connection: initialized_connections.append(
            received_connection
        ),
    )

    def fake_process_job(
        received_connection: Any,
        job: Job,
    ) -> JobProcessingResult:
        assert received_connection is connection
        processed_jobs.append(job)
        return JobProcessingResult(status=next(statuses), job=job)

    monkeypatch.setattr(main_module, "process_job", fake_process_job)
    monkeypatch.setattr(
        main_module,
        "send_job_notification",
        lambda settings, scored_job: notified_jobs.append(scored_job.job),
    )

    summary = run_monitor(
        tags=("python",),
        limit=3,
        criteria=JobFilterCriteria(excluded_keywords=("vaga 3",)),
        scoring_keywords=("vaga 1",),
        notification_settings=TelegramSettings("test-token", "123"),
    )

    assert summary == MonitorSummary(
        fetched=4,
        relevant=3,
        processed=3,
        top_score=3,
        inserted=1,
        duplicates=1,
        invalid=1,
        notifications_sent=1,
        notification_failures=0,
    )
    assert initialized_connections == [connection]
    assert processed_jobs == [jobs[1], jobs[0], jobs[2]]
    assert notified_jobs == [jobs[1]]
    assert connection.was_closed is True


def test_run_monitor_counts_notification_failure_without_stopping(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Mantém a vaga inserida quando o Telegram está indisponível."""
    job = _create_job(1)
    connection = FakeConnection()
    monkeypatch.setattr(main_module, "fetch_remote_ok_jobs", lambda *, tags: [job])
    monkeypatch.setattr(main_module, "fetch_remotive_jobs", lambda: [])
    monkeypatch.setattr(main_module, "load_database_settings", lambda: object())
    monkeypatch.setattr(main_module, "connect_database", lambda settings: connection)
    monkeypatch.setattr(main_module, "initialize_database", lambda connection: None)
    monkeypatch.setattr(
        main_module,
        "process_job",
        lambda connection, received_job: JobProcessingResult(
            status=JobProcessingStatus.INSERTED,
            job=received_job,
        ),
    )

    def fail_notification(settings: Any, scored_job: Any) -> None:
        raise TelegramNotificationError("Telegram indisponível")

    monkeypatch.setattr(main_module, "send_job_notification", fail_notification)

    summary = run_monitor(
        limit=1,
        notification_settings=TelegramSettings("test-token", "123"),
    )

    assert summary.inserted == 1
    assert summary.notifications_sent == 0
    assert summary.notification_failures == 1
    assert connection.was_closed is True


def test_run_monitor_closes_connection_when_processing_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Fecha a conexão mesmo quando um componente gera uma exceção."""
    connection = FakeConnection()
    monkeypatch.setattr(
        main_module,
        "fetch_remote_ok_jobs",
        lambda *, tags: [_create_job(1)],
    )
    monkeypatch.setattr(main_module, "fetch_remotive_jobs", lambda: [])
    monkeypatch.setattr(main_module, "load_database_settings", lambda: object())
    monkeypatch.setattr(
        main_module,
        "connect_database",
        lambda settings: connection,
    )
    monkeypatch.setattr(main_module, "initialize_database", lambda connection: None)

    def fail_processing(connection: Any, job: Job) -> JobProcessingResult:
        raise RuntimeError("failure")

    monkeypatch.setattr(main_module, "process_job", fail_processing)

    with pytest.raises(RuntimeError, match="failure"):
        run_monitor(limit=1)

    assert connection.was_closed is True


def test_run_monitor_rejects_invalid_limit_before_external_calls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Rejeita limite inválido antes de acessar API ou banco."""
    external_call_was_made = False

    def fake_fetch(*, tags: tuple[str, ...]) -> list[Job]:
        nonlocal external_call_was_made
        external_call_was_made = True
        return []

    monkeypatch.setattr(main_module, "fetch_remote_ok_jobs", fake_fetch)

    with pytest.raises(ValueError, match="O limite deve ser maior que zero"):
        run_monitor(limit=0)

    assert external_call_was_made is False
