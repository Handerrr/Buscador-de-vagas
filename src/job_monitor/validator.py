"""Validação dos dados de vagas."""

from datetime import datetime
from urllib.parse import urlparse

from job_monitor.models import Job


def _is_blank(value: str) -> bool:
    """Indica se um texto não possui conteúdo útil."""
    return not value.strip()


def _is_valid_web_url(value: str) -> bool:
    """Indica se o texto possui o formato básico de uma URL HTTP ou HTTPS."""
    if any(character.isspace() for character in value):
        return False

    parsed_url = urlparse(value)
    return parsed_url.scheme in {"http", "https"} and bool(parsed_url.netloc)


def _has_timezone(value: datetime) -> bool:
    """Indica se uma data possui informação válida de fuso horário."""
    return value.tzinfo is not None and value.utcoffset() is not None


def validate_job(job: Job) -> list[str]:
    """Retorna todos os problemas encontrados nos dados de uma vaga."""
    errors: list[str] = []

    if _is_blank(job.title):
        errors.append("O título da vaga é obrigatório.")

    if _is_blank(job.company):
        errors.append("A empresa da vaga é obrigatória.")

    if _is_blank(job.source):
        errors.append("A fonte da vaga é obrigatória.")

    if _is_blank(job.url):
        errors.append("A URL da vaga é obrigatória.")
    elif not _is_valid_web_url(job.url):
        errors.append("A URL da vaga deve usar HTTP ou HTTPS e possuir um domínio.")

    if job.published_at is not None and not _has_timezone(job.published_at):
        errors.append("A data de publicação deve possuir fuso horário.")

    if not _has_timezone(job.collected_at):
        errors.append("A data de coleta deve possuir fuso horário.")

    return errors

