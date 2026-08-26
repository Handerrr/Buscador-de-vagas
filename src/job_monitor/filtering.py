"""Filtragem de vagas segundo critérios definidos pelo usuário."""

import re
import unicodedata
from dataclasses import dataclass
from enum import StrEnum

from job_monitor.models import Job


class JobLevel(StrEnum):
    """Níveis de senioridade reconhecidos pelo monitor."""

    INTERNSHIP = "internship"
    JUNIOR = "junior"
    MID_LEVEL = "mid_level"
    SENIOR = "senior"


@dataclass(frozen=True)
class JobFilterCriteria:
    """Critérios opcionais utilizados para considerar uma vaga relevante."""

    title_keywords: tuple[str, ...] = ()
    included_keywords: tuple[str, ...] = ()
    excluded_keywords: tuple[str, ...] = ()
    locations: tuple[str, ...] = ()
    levels: tuple[JobLevel, ...] = ()


def normalize_for_search(value: str) -> str:
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
    normalized_values = (normalize_for_search(value) for value in values)
    return tuple(value for value in normalized_values if value)


def _location_matches(location: str, accepted_locations: tuple[str, ...]) -> bool:
    """Reconhece regiões remotas que permitem trabalhar a partir do Brasil."""
    if any(accepted_location in location for accepted_location in accepted_locations):
        return True

    brazil_is_requested = any(
        accepted_location in {"brasil", "brazil"}
        for accepted_location in accepted_locations
    )
    brazil_eligible_regions = (
        "worldwide",
        "anywhere",
        "global",
        "americas",
        "latin america",
        "south america",
    )
    return brazil_is_requested and any(
        region in location for region in brazil_eligible_regions
    )


def parse_job_level(value: str) -> JobLevel:
    """Converte um nome de nível em um valor reconhecido pelo monitor."""
    normalized_value = normalize_for_search(value)
    level_names = {
        "estagio": JobLevel.INTERNSHIP,
        "estagiario": JobLevel.INTERNSHIP,
        "intern": JobLevel.INTERNSHIP,
        "internship": JobLevel.INTERNSHIP,
        "junior": JobLevel.JUNIOR,
        "jr": JobLevel.JUNIOR,
        "pleno": JobLevel.MID_LEVEL,
        "mid": JobLevel.MID_LEVEL,
        "mid-level": JobLevel.MID_LEVEL,
        "senior": JobLevel.SENIOR,
        "sr": JobLevel.SENIOR,
    }

    try:
        return level_names[normalized_value]
    except KeyError as error:
        raise ValueError(f"Nível de vaga não reconhecido: {value}") from error


def infer_job_level(job: Job) -> JobLevel | None:
    """Infere o nível quando ele está declarado no título da vaga."""
    normalized_title = normalize_for_search(job.title)
    aliases = (
        (JobLevel.INTERNSHIP, ("estagio", "estagiario", "intern", "internship")),
        (JobLevel.JUNIOR, ("junior", "jr")),
        (JobLevel.MID_LEVEL, ("pleno", "mid-level", "mid level")),
        (JobLevel.SENIOR, ("senior", "sr")),
    )

    for level, level_aliases in aliases:
        if any(
            re.search(rf"\b{re.escape(alias)}\b", normalized_title)
            for alias in level_aliases
        ):
            return level

    return None


def is_relevant(job: Job, criteria: JobFilterCriteria) -> bool:
    """Indica se uma vaga atende a todos os critérios configurados."""
    searchable_text = normalize_for_search(
        " ".join((job.title, job.description or ""))
    )
    location = normalize_for_search(job.location or "")
    title = normalize_for_search(job.title)
    title_keywords = _normalize_criteria(criteria.title_keywords)
    included_keywords = _normalize_criteria(criteria.included_keywords)
    excluded_keywords = _normalize_criteria(criteria.excluded_keywords)
    accepted_locations = _normalize_criteria(criteria.locations)
    job_level = infer_job_level(job)

    if any(keyword in searchable_text for keyword in excluded_keywords):
        return False

    if title_keywords and not any(keyword in title for keyword in title_keywords):
        return False

    if included_keywords and not any(
        keyword in searchable_text for keyword in included_keywords
    ):
        return False

    if accepted_locations and not _location_matches(location, accepted_locations):
        return False

    if criteria.levels and job_level is not None and job_level not in criteria.levels:
        return False

    return True


def filter_jobs(jobs: list[Job], criteria: JobFilterCriteria) -> list[Job]:
    """Retorna somente as vagas que atendem aos critérios."""
    return [job for job in jobs if is_relevant(job, criteria)]
