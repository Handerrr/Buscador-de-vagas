"""Testes dos modelos de dados do projeto."""

from datetime import UTC

from job_monitor import Job


def test_create_job_with_required_fields() -> None:
    """Cria uma vaga mesmo quando os campos opcionais não são informados."""
    job = Job(
        title="Pessoa Desenvolvedora Python",
        company="Empresa Exemplo",
        url="https://example.com/jobs/123",
        source="Fonte Exemplo",
    )

    assert job.title == "Pessoa Desenvolvedora Python"
    assert job.company == "Empresa Exemplo"
    assert job.url == "https://example.com/jobs/123"
    assert job.source == "Fonte Exemplo"
    assert job.location is None
    assert job.description is None
    assert job.published_at is None
    assert job.collected_at.tzinfo is UTC

