"""Execução periódica do monitor em ambientes como Docker."""

import os
import signal
from collections.abc import Callable
from threading import Event

from psycopg import Error as DatabaseError

from job_monitor.config import (
    load_job_filter_criteria,
    load_job_scoring_keywords,
    load_telegram_settings,
)
from job_monitor.main import MonitorSummary, run_monitor
from job_monitor.scraper import RemoteOKError


DEFAULT_INTERVAL_MINUTES = 60
MINIMUM_INTERVAL_MINUTES = 15


def load_worker_interval_minutes() -> int:
    """Lê e valida o intervalo configurado para as coletas."""
    interval_text = os.getenv(
        "MONITOR_INTERVAL_MINUTES",
        str(DEFAULT_INTERVAL_MINUTES),
    )

    try:
        interval = int(interval_text)
    except ValueError as error:
        raise ValueError("MONITOR_INTERVAL_MINUTES deve ser um número inteiro.") from error

    if interval < MINIMUM_INTERVAL_MINUTES:
        raise ValueError(
            f"MONITOR_INTERVAL_MINUTES deve ser no mínimo {MINIMUM_INTERVAL_MINUTES}."
        )

    return interval


def print_summary(summary: MonitorSummary) -> None:
    """Exibe no log os contadores de uma coleta concluída."""
    print("Monitor executado com sucesso:", flush=True)
    print(f"  Recebidas da API: {summary.fetched}", flush=True)
    print(f"  Relevantes: {summary.relevant}", flush=True)
    print(f"  Processadas: {summary.processed}", flush=True)
    print(f"  Inseridas: {summary.inserted}", flush=True)
    print(f"  Duplicadas: {summary.duplicates}", flush=True)
    print(f"  Inválidas: {summary.invalid}", flush=True)
    print(f"  Notificações enviadas: {summary.notifications_sent}", flush=True)
    print(f"  Falhas de notificação: {summary.notification_failures}", flush=True)


def execute_monitor_cycle() -> int:
    """Executa uma coleta usando as configurações do ambiente."""
    try:
        summary = run_monitor(
            criteria=load_job_filter_criteria(),
            scoring_keywords=load_job_scoring_keywords(),
            notification_settings=load_telegram_settings(),
        )
    except (DatabaseError, RemoteOKError, ValueError) as error:
        print(f"Falha ao executar o monitor: {error}", flush=True)
        return 1

    print_summary(summary)
    return 0


def run_worker(
    *,
    interval_minutes: int,
    stop_event: Event,
    execute_cycle: Callable[[], int] = execute_monitor_cycle,
) -> None:
    """Executa ciclos até que o processo receba um pedido de parada."""
    while not stop_event.is_set():
        execute_cycle()
        stop_event.wait(interval_minutes * 60)


def main() -> int:
    """Inicia o worker e trata os sinais de encerramento do contêiner."""
    try:
        interval_minutes = load_worker_interval_minutes()
    except ValueError as error:
        print(f"Configuração inválida do worker: {error}", flush=True)
        return 1

    stop_event = Event()

    def request_stop(signum: int, frame: object) -> None:
        stop_event.set()

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    print(
        f"Worker iniciado com intervalo de {interval_minutes} minutos.",
        flush=True,
    )
    run_worker(interval_minutes=interval_minutes, stop_event=stop_event)
    print("Worker encerrado.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
