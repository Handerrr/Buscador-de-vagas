"""Ponto de entrada e coordenação do monitor de vagas."""

import argparse
from dataclasses import dataclass

from psycopg import Error as DatabaseError

from job_monitor.config import (
    TelegramSettings,
    load_database_settings,
    load_job_filter_criteria,
    load_job_scoring_keywords,
    load_telegram_settings,
)
from job_monitor.database import connect_database, initialize_database
from job_monitor.filtering import JobFilterCriteria, filter_jobs, parse_job_level
from job_monitor.notifier import TelegramNotificationError, send_job_notification
from job_monitor.scraper import (
    RemoteOKError,
    RemotiveError,
    fetch_remote_ok_jobs,
    fetch_remotive_jobs,
)
from job_monitor.scoring import rank_jobs
from job_monitor.service import JobProcessingStatus, process_job


DEFAULT_TAGS = ("python", "data")
DEFAULT_LIMIT = 50


@dataclass(frozen=True)
class MonitorSummary:
    """Contadores produzidos por uma execução do monitor."""

    fetched: int
    relevant: int
    processed: int
    top_score: int
    inserted: int
    duplicates: int
    invalid: int
    notifications_sent: int
    notification_failures: int


def run_monitor(
    *,
    tags: tuple[str, ...] = DEFAULT_TAGS,
    limit: int = DEFAULT_LIMIT,
    criteria: JobFilterCriteria | None = None,
    scoring_keywords: tuple[str, ...] = (),
    notification_settings: TelegramSettings | None = None,
) -> MonitorSummary:
    """Coleta, processa e armazena vagas de todas as fontes configuradas."""
    if limit <= 0:
        raise ValueError("O limite deve ser maior que zero.")

    jobs = [*fetch_remote_ok_jobs(tags=tags), *fetch_remotive_jobs()]
    relevant_jobs = filter_jobs(jobs, criteria or JobFilterCriteria())
    ranked_jobs = rank_jobs(relevant_jobs, scoring_keywords)
    ranked_jobs_to_process = ranked_jobs[:limit]
    connection = connect_database(load_database_settings())
    inserted = 0
    duplicates = 0
    invalid = 0
    notifications_sent = 0
    notification_failures = 0

    try:
        initialize_database(connection)

        for scored_job in ranked_jobs_to_process:
            result = process_job(connection, scored_job.job)

            if result.status is JobProcessingStatus.INSERTED:
                inserted += 1
                if notification_settings is not None:
                    try:
                        send_job_notification(notification_settings, scored_job)
                        notifications_sent += 1
                    except TelegramNotificationError:
                        notification_failures += 1
            elif result.status is JobProcessingStatus.DUPLICATE:
                duplicates += 1
            else:
                invalid += 1
    finally:
        connection.close()

    return MonitorSummary(
        fetched=len(jobs),
        relevant=len(relevant_jobs),
        processed=len(ranked_jobs_to_process),
        top_score=ranked_jobs[0].score if ranked_jobs else 0,
        inserted=inserted,
        duplicates=duplicates,
        invalid=invalid,
        notifications_sent=notifications_sent,
        notification_failures=notification_failures,
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
        "--preferred-keywords",
        nargs="+",
        default=None,
        help="tecnologias e termos usados para pontuar as vagas",
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
    parser.add_argument(
        "--no-notifications",
        action="store_true",
        help="executa o monitor sem enviar mensagens pelo Telegram",
    )
    return parser


def main() -> int:
    """Executa a interface de terminal e retorna seu código de saída."""
    arguments = _create_argument_parser().parse_args()

    try:
        configured_criteria = load_job_filter_criteria()
        configured_scoring_keywords = load_job_scoring_keywords()
        notification_settings = (
            None if arguments.no_notifications else load_telegram_settings()
        )
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
            scoring_keywords=(
                tuple(arguments.preferred_keywords)
                if arguments.preferred_keywords is not None
                else configured_scoring_keywords
            ),
            notification_settings=notification_settings,
        )
    except (DatabaseError, RemoteOKError, RemotiveError, ValueError) as error:
        print(f"Falha ao executar o monitor: {error}")
        return 1

    print("Monitor executado com sucesso:")
    print(f"  Recebidas da API: {summary.fetched}")
    print(f"  Relevantes: {summary.relevant}")
    print(f"  Processadas: {summary.processed}")
    print(f"  Maior pontuação: {summary.top_score}")
    print(f"  Inseridas: {summary.inserted}")
    print(f"  Duplicadas: {summary.duplicates}")
    print(f"  Inválidas: {summary.invalid}")
    print(f"  Notificações enviadas: {summary.notifications_sent}")
    print(f"  Falhas de notificação: {summary.notification_failures}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
