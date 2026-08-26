"""Criação de conexões com o PostgreSQL."""

from typing import Any

from job_monitor.config import DatabaseSettings


def connect_database(settings: DatabaseSettings) -> Any:
    """Abre e devolve uma conexão com o PostgreSQL."""
    import psycopg

    if settings.connection_url is not None:
        return psycopg.connect(settings.connection_url)

    return psycopg.connect(
        host=settings.host,
        port=settings.port,
        dbname=settings.name,
        user=settings.user,
        password=settings.password,
    )
