"""Operações de armazenamento e consulta de vagas."""

from typing import Any

from job_monitor.deduplication import generate_job_key
from job_monitor.models import Job


INSERT_JOB = """
INSERT INTO jobs (
    job_key,
    title,
    company,
    url,
    source,
    location,
    description,
    published_at,
    collected_at
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (job_key) DO NOTHING
RETURNING id;
"""


def save_job(connection: Any, job: Job) -> bool:
    """Armazena uma vaga e informa se um novo registro foi inserido."""
    parameters = (
        generate_job_key(job),
        job.title,
        job.company,
        job.url,
        job.source,
        job.location,
        job.description,
        job.published_at,
        job.collected_at,
    )
    cursor = connection.execute(INSERT_JOB, parameters)

    return cursor.fetchone() is not None

