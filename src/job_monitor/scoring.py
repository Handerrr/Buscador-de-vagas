"""Pontuação e ordenação das vagas relevantes."""

from dataclasses import dataclass

from job_monitor.filtering import normalize_for_search
from job_monitor.models import Job


TITLE_MATCH_POINTS = 3
DESCRIPTION_MATCH_POINTS = 1


@dataclass(frozen=True)
class ScoredJob:
    """Vaga acompanhada de sua pontuação e dos termos encontrados."""

    job: Job
    score: int
    matched_keywords: tuple[str, ...]


def score_job(job: Job, preferred_keywords: tuple[str, ...]) -> ScoredJob:
    """Calcula a relevância de uma vaga a partir de termos preferidos."""
    title = normalize_for_search(job.title)
    description = normalize_for_search(job.description or "")
    score = 0
    matched_keywords: list[str] = []
    seen_keywords: set[str] = set()

    for keyword in preferred_keywords:
        normalized_keyword = normalize_for_search(keyword)
        if not normalized_keyword or normalized_keyword in seen_keywords:
            continue

        seen_keywords.add(normalized_keyword)
        if normalized_keyword in title:
            score += TITLE_MATCH_POINTS
            matched_keywords.append(keyword.strip())
        elif normalized_keyword in description:
            score += DESCRIPTION_MATCH_POINTS
            matched_keywords.append(keyword.strip())

    return ScoredJob(
        job=job,
        score=score,
        matched_keywords=tuple(matched_keywords),
    )


def rank_jobs(jobs: list[Job], preferred_keywords: tuple[str, ...]) -> list[ScoredJob]:
    """Ordena vagas da maior para a menor pontuação."""
    scored_jobs = [score_job(job, preferred_keywords) for job in jobs]
    return sorted(scored_jobs, key=lambda scored_job: scored_job.score, reverse=True)

