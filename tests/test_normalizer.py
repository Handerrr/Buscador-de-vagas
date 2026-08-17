"""Testes da normalização dos dados de vagas."""

from datetime import UTC, datetime

from job_monitor import Job, normalize_job


def test_normalize_job_text_fields() -> None:
    """Remove espaços excedentes dos campos textuais de uma vaga."""
    collected_at = datetime(2026, 8, 17, 12, 0, tzinfo=UTC)
    job = Job(
        title="  Pessoa   Desenvolvedora\tPython  ",
        company="  Empresa\nExemplo ",
        url="  https://example.com/jobs/123  ",
        source="  Fonte   Exemplo ",
        location="  São   Paulo, SP  ",
        description=" Desenvolver\nsoluções   em Python. ",
        collected_at=collected_at,
    )

    normalized_job = normalize_job(job)

    assert normalized_job.title == "Pessoa Desenvolvedora Python"
    assert normalized_job.company == "Empresa Exemplo"
    assert normalized_job.url == "https://example.com/jobs/123"
    assert normalized_job.source == "Fonte Exemplo"
    assert normalized_job.location == "São Paulo, SP"
    assert normalized_job.description == "Desenvolver soluções em Python."
    assert normalized_job.collected_at == collected_at


def test_normalize_job_converts_empty_optional_fields_to_none() -> None:
    """Converte campos opcionais sem conteúdo em ``None``."""
    job = Job(
        title="Analista de Dados",
        company="Empresa Exemplo",
        url="https://example.com/jobs/456",
        source="Fonte Exemplo",
        location="   ",
        description="\n\t",
    )

    normalized_job = normalize_job(job)

    assert normalized_job.location is None
    assert normalized_job.description is None


def test_normalize_job_does_not_change_original_job() -> None:
    """Mantém intactos os dados do objeto recebido."""
    job = Job(
        title="  Engenheira de Dados  ",
        company="Empresa Exemplo",
        url="https://example.com/jobs/789",
        source="Fonte Exemplo",
    )

    normalized_job = normalize_job(job)

    assert normalized_job is not job
    assert job.title == "  Engenheira de Dados  "
    assert normalized_job.title == "Engenheira de Dados"

