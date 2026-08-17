"""Normalização dos dados coletados de vagas."""

from dataclasses import replace

from job_monitor.models import Job


def _normalize_text(value: str) -> str:
    """Remove espaços excedentes de um texto."""
    return " ".join(value.split())


def _normalize_optional_text(value: str | None) -> str | None:
    """Normaliza um texto opcional e converte conteúdo vazio em ``None``."""
    if value is None:
        return None

    normalized_value = _normalize_text(value)
    return normalized_value or None


def normalize_job(job: Job) -> Job:
    """Devolve uma nova vaga com seus campos textuais normalizados."""
    return replace(
        job,
        title=_normalize_text(job.title),
        company=_normalize_text(job.company),
        url=job.url.strip(),
        source=_normalize_text(job.source),
        location=_normalize_optional_text(job.location),
        description=_normalize_optional_text(job.description),
    )

