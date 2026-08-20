"""Teste de integração do repositório com o PostgreSQL local."""

import os
from uuid import uuid4

import pytest

from job_monitor import (
    Job,
    JobProcessingStatus,
    generate_job_key,
    load_database_settings,
    process_job,
)
from job_monitor.database import connect_database, find_job_by_key


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("RUN_DATABASE_INTEGRATION") != "1",
        reason="Teste de integração com PostgreSQL não solicitado.",
    ),
]


class RollbackIntegrationTest(Exception):
    """Interrompe a transação para remover os dados criados pelo teste."""


def test_save_job_and_prevent_duplicate_in_postgresql() -> None:
    """Insere uma vaga, rejeita sua duplicata e desfaz a inserção."""
    connection = connect_database(load_database_settings())
    job = Job(
        title="Vaga temporária de integração",
        company="Empresa de Teste",
        url=f"https://integration.test/jobs/{uuid4()}",
        source="Teste de Integração",
    )
    job_key = generate_job_key(job)

    try:
        try:
            with connection.transaction():
                first_result = process_job(connection, job)
                second_result = process_job(connection, job)

                assert first_result.status is JobProcessingStatus.INSERTED
                assert second_result.status is JobProcessingStatus.DUPLICATE
                assert find_job_by_key(connection, job_key) == job
                raise RollbackIntegrationTest
        except RollbackIntegrationTest:
            pass

        stored_count = connection.execute(
            "SELECT COUNT(*) FROM jobs WHERE job_key = %s",
            (job_key,),
        ).fetchone()[0]

        assert stored_count == 0
    finally:
        connection.close()
