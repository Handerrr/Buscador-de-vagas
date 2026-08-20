"""Ponto de entrada e coordenação do monitor de vagas."""

import argparse
from dataclasses import dataclass

from psycopg import Error as DatabaseError

from job_monitor.config import load_database_settings
from job_monitor.database import connect_database, initialize_database
from job_monitor.scraper import RemoteOKError, fetch_remote_ok_jobs
from job_monitor.service import JobProcessingStatus, process_job


DEFAULT_TAGS = ("python", "data")
DEFAULT_LIMIT = 50


@dataclass(frozen=True)
class MonitorSummary:
    """Contadores produzidos por uma execução do monitor."""

    fetched: int
    processed: int
    inserted: int
    duplicates: int
    invalid: int


def run_monitor(
    *,
    tags: tuple[str, ...] = DEFAULT_TAGS,
    limit: int = DEFAULT_LIMIT,
) -> MonitorSummary:
    """Coleta, processa e armazena vagas do Remote OK."""
    if limit <= 0:
        raise ValueError("O limite deve ser maior que zero.")

    jobs = fetch_remote_ok_jobs(tags=tags)
    jobs_to_process = jobs[:limit]
    connection = connect_database(load_database_settings())
    inserted = 0
    duplicates = 0
    invalid = 0

    try:
        initialize_database(connection)

        for job in jobs_to_process:
            result = process_job(connection, job)

            if result.status is JobProcessingStatus.INSERTED:
                inserted += 1
            elif result.status is JobProcessingStatus.DUPLICATE:
                duplicates += 1
            else:
                invalid += 1
    finally:
        connection.close()

    return MonitorSummary(
        fetched=len(jobs),
        processed=len(jobs_to_process),
        inserted=inserted,
        duplicates=duplicates,
        invalid=invalid,
    )


def _create_argument_parser() -> argparse.ArgumentParser:
    """Cria os argumentos aceitos pela interface de terminal."""
    parser = argparse.ArgumentParser(description="Monitor inteligente de vagas")
    parser.add_argument(
        "--tags",
        nargs="+",
        default=list(DEFAULT_TAGS),
        help="tags usadas para filtrar as vagas no Remote OK",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_LIMIT,
        help="quantidade máxima de vagas processadas",
    )
    return parser


def main() -> int:
    """Executa a interface de terminal e retorna seu código de saída."""
    arguments = _create_argument_parser().parse_args()

    try:
        summary = run_monitor(tags=tuple(arguments.tags), limit=arguments.limit)
    except (DatabaseError, RemoteOKError, ValueError) as error:
        print(f"Falha ao executar o monitor: {error}")
        return 1

    print("Monitor executado com sucesso:")
    print(f"  Recebidas da API: {summary.fetched}")
    print(f"  Processadas: {summary.processed}")
    print(f"  Inseridas: {summary.inserted}")
    print(f"  Duplicadas: {summary.duplicates}")
    print(f"  Inválidas: {summary.invalid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
