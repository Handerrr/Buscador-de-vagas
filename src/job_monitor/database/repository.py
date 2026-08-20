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

SELECT_JOB_BY_KEY = """
SELECT
    title,
    company,
    url,
    source,
    location,
    description,
    published_at,
    collected_at
FROM jobs
WHERE job_key = %s;
"""

LIST_JOBS = """
SELECT
    title,
    company,
    url,
    source,
    location,
    description,
    published_at,
    collected_at
FROM jobs
ORDER BY collected_at DESC, id DESC
LIMIT %s;
"""


def _row_to_job(row: tuple[Any, ...]) -> Job:
    """Converte uma linha retornada pelo PostgreSQL em uma vaga."""
    return Job(
        title=row[0],
        company=row[1],
        url=row[2],
        source=row[3],
        location=row[4],
        description=row[5],
        published_at=row[6],
        collected_at=row[7],
    )


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


def find_job_by_key(connection: Any, job_key: str) -> Job | None:
    """Busca uma vaga por sua chave de duplicidade."""
    row = connection.execute(SELECT_JOB_BY_KEY, (job_key,)).fetchone()

    if row is None:
        return None

    return _row_to_job(row)


def list_jobs(connection: Any, *, limit: int = 100) -> list[Job]:
    """Lista as vagas mais recentes até o limite informado."""
    if limit <= 0:
        raise ValueError("O limite deve ser maior que zero.")

    rows = connection.execute(LIST_JOBS, (limit,)).fetchall()
    return [_row_to_job(row) for row in rows]
