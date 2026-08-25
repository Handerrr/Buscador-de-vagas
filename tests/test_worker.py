"""Testes do processo periódico usado no Docker."""

from threading import Event

import pytest

from job_monitor import worker


def test_load_worker_interval_minutes(monkeypatch: pytest.MonkeyPatch) -> None:
    """Converte o intervalo informado no ambiente."""
    monkeypatch.setenv("MONITOR_INTERVAL_MINUTES", "30")

    assert worker.load_worker_interval_minutes() == 30


@pytest.mark.parametrize("value", ["texto", "14"])
def test_load_worker_interval_rejects_invalid_value(
    monkeypatch: pytest.MonkeyPatch,
    value: str,
) -> None:
    """Evita ciclos excessivos ou configurações que não sejam números."""
    monkeypatch.setenv("MONITOR_INTERVAL_MINUTES", value)

    with pytest.raises(ValueError):
        worker.load_worker_interval_minutes()


def test_run_worker_executes_immediately_and_waits() -> None:
    """Executa um ciclo antes de aguardar o intervalo configurado."""
    stop_event = Event()
    executions = 0

    def execute_cycle() -> int:
        nonlocal executions
        executions += 1
        stop_event.set()
        return 0

    worker.run_worker(
        interval_minutes=60,
        stop_event=stop_event,
        execute_cycle=execute_cycle,
    )

    assert executions == 1
