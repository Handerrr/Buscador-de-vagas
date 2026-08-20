"""Coordenação do fluxo de processamento das vagas."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from job_monitor.database.repository import save_job
from job_monitor.models import Job
from job_monitor.normalizer import normalize_job
from job_monitor.validator import validate_job


class JobProcessingStatus(StrEnum):
    """Possíveis resultados do processamento de uma vaga."""

    INSERTED = "inserted"
    DUPLICATE = "duplicate"
    INVALID = "invalid"


@dataclass(frozen=True)
class JobProcessingResult:
    """Resultado completo do processamento de uma vaga."""

    status: JobProcessingStatus
    job: Job
    errors: tuple[str, ...] = ()


def process_job(connection: Any, job: Job) -> JobProcessingResult:
    """Normaliza, valida e tenta armazenar uma vaga."""
    normalized_job = normalize_job(job)
    errors = tuple(validate_job(normalized_job))

    if errors:
        return JobProcessingResult(
            status=JobProcessingStatus.INVALID,
            job=normalized_job,
            errors=errors,
        )

    with connection.transaction():
        was_inserted = save_job(connection, normalized_job)

    status = (
        JobProcessingStatus.INSERTED
        if was_inserted
        else JobProcessingStatus.DUPLICATE
    )
    return JobProcessingResult(status=status, job=normalized_job)

