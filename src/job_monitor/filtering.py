"""Filtragem de vagas segundo critérios definidos pelo usuário."""

import unicodedata
from dataclasses import dataclass

from job_monitor.models import Job


@dataclass(frozen=True)
class JobFilterCriteria:
    """Critérios opcionais utilizados para considerar uma vaga relevante."""

    included_keywords: tuple[str, ...] = ()
    excluded_keywords: tuple[str, ...] = ()
    locations: tuple[str, ...] = ()


def _normalize_for_search(value: str) -> str:
    """Padroniza caixa, acentos e espaços para comparação textual."""
    decomposed_value = unicodedata.normalize("NFKD", value.casefold())
    without_accents = "".join(
        character
        for character in decomposed_value
        if not unicodedata.combining(character)
    )
    return " ".join(without_accents.split())


def _normalize_criteria(values: tuple[str, ...]) -> tuple[str, ...]:
    """Normaliza critérios e descarta valores sem conteúdo."""
    normalized_values = (_normalize_for_search(value) for value in values)
    return tuple(value for value in normalized_values if value)


def is_relevant(job: Job, criteria: JobFilterCriteria) -> bool:
    """Indica se uma vaga atende a todos os critérios configurados."""
    searchable_text = _normalize_for_search(
        " ".join((job.title, job.description or ""))
    )
    location = _normalize_for_search(job.location or "")
    included_keywords = _normalize_criteria(criteria.included_keywords)
    excluded_keywords = _normalize_criteria(criteria.excluded_keywords)
    accepted_locations = _normalize_criteria(criteria.locations)

    if any(keyword in searchable_text for keyword in excluded_keywords):
        return False

    if included_keywords and not any(
        keyword in searchable_text for keyword in included_keywords
    ):
        return False

    if accepted_locations and not any(
        accepted_location in location for accepted_location in accepted_locations
    ):
        return False

    return True


def filter_jobs(jobs: list[Job], criteria: JobFilterCriteria) -> list[Job]:
    """Retorna somente as vagas que atendem aos critérios."""
    return [job for job in jobs if is_relevant(job, criteria)]

