"""Definição e inicialização das tabelas do PostgreSQL."""

from typing import Any


CREATE_JOBS_TABLE = """
CREATE TABLE IF NOT EXISTS jobs (
    id BIGSERIAL PRIMARY KEY,
    job_key VARCHAR(64) NOT NULL UNIQUE,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    url TEXT NOT NULL,
    source TEXT NOT NULL,
    location TEXT,
    description TEXT,
    published_at TIMESTAMPTZ,
    collected_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def initialize_database(connection: Any) -> None:
    """Cria as tabelas necessárias caso elas ainda não existam."""
    with connection.transaction():
        connection.execute(CREATE_JOBS_TABLE)

