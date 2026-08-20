"""Ponto de entrada e coordenação do monitor de vagas."""

import argparse
from dataclasses import dataclass

from psycopg import Error as DatabaseError

from job_monitor.config import load_database_settings, load_job_filter_criteria
from job_monitor.database import connect_database, initialize_database
from job_monitor.filtering import JobFilterCriteria, filter_jobs, parse_job_level
from job_monitor.scraper import RemoteOKError, fetch_remote_ok_jobs
from job_monitor.service import JobProcessingStatus, process_job


DEFAULT_TAGS = ("python", "data")
DEFAULT_LIMIT = 50


@dataclass(frozen=True)
class MonitorSummary:
    """Contadores produzidos por uma execução do monitor."""

    fetched: int
    relevant: int
    processed: int
    inserted: int
    duplicates: int
    invalid: int


def run_monitor(
    *,
    tags: tuple[str, ...] = DEFAULT_TAGS,
    limit: int = DEFAULT_LIMIT,
    criteria: JobFilterCriteria | None = None,
) -> MonitorSummary:
    """Coleta, processa e armazena vagas do Remote OK."""
    if limit <= 0:
        raise ValueError("O limite deve ser maior que zero.")

    jobs = fetch_remote_ok_jobs(tags=tags)
    relevant_jobs = filter_jobs(jobs, criteria or JobFilterCriteria())
    jobs_to_process = relevant_jobs[:limit]
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
        relevant=len(relevant_jobs),
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
    parser.add_argument(
        "--titles",
        nargs="+",
        default=None,
        help="títulos de cargos aceitos",
    )
    parser.add_argument(
        "--include-keywords",
        nargs="+",
        default=None,
        help="palavras desejadas no título ou na descrição",
    )
    parser.add_argument(
        "--exclude-keywords",
        nargs="+",
        default=None,
        help="palavras que tornam uma vaga irrelevante",
    )
    parser.add_argument(
        "--locations",
        nargs="+",
        default=None,
        help="localidades aceitas",
    )
    parser.add_argument(
        "--levels",
        nargs="+",
        default=None,
        help="níveis aceitos: estágio, júnior, pleno e sênior",
    )
    return parser


def main() -> int:
    """Executa a interface de terminal e retorna seu código de saída."""
    arguments = _create_argument_parser().parse_args()

    try:
        configured_criteria = load_job_filter_criteria()
        criteria = JobFilterCriteria(
            title_keywords=(
                tuple(arguments.titles)
                if arguments.titles is not None
                else configured_criteria.title_keywords
            ),
            included_keywords=(
                tuple(arguments.include_keywords)
                if arguments.include_keywords is not None
                else configured_criteria.included_keywords
            ),
            excluded_keywords=(
                tuple(arguments.exclude_keywords)
                if arguments.exclude_keywords is not None
                else configured_criteria.excluded_keywords
            ),
            locations=(
                tuple(arguments.locations)
                if arguments.locations is not None
                else configured_criteria.locations
            ),
            levels=(
                tuple(parse_job_level(level) for level in arguments.levels)
                if arguments.levels is not None
                else configured_criteria.levels
            ),
        )
        summary = run_monitor(
            tags=tuple(arguments.tags),
            limit=arguments.limit,
            criteria=criteria,
        )
    except (DatabaseError, RemoteOKError, ValueError) as error:
        print(f"Falha ao executar o monitor: {error}")
        return 1

    print("Monitor executado com sucesso:")
    print(f"  Recebidas da API: {summary.fetched}")
    print(f"  Relevantes: {summary.relevant}")
    print(f"  Processadas: {summary.processed}")
    print(f"  Inseridas: {summary.inserted}")
    print(f"  Duplicadas: {summary.duplicates}")
    print(f"  Inválidas: {summary.invalid}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
