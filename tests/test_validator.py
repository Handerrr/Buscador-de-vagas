"""Testes da validação dos dados de vagas."""

from datetime import UTC, datetime

from job_monitor import Job, validate_job


def test_valid_job_has_no_errors() -> None:
    """Não retorna erros quando todos os dados são válidos."""
    job = Job(
        title="Pessoa Desenvolvedora Python",
        company="Empresa Exemplo",
        url="https://example.com/jobs/123",
        source="Fonte Exemplo",
        published_at=datetime(2026, 8, 17, 9, 0, tzinfo=UTC),
    )

    assert validate_job(job) == []


def test_required_fields_report_all_errors() -> None:
    """Informa de uma vez todos os campos obrigatórios sem conteúdo."""
    job = Job(title=" ", company="", url="\t", source="  ")

    errors = validate_job(job)

    assert errors == [
        "O título da vaga é obrigatório.",
        "A empresa da vaga é obrigatória.",
        "A fonte da vaga é obrigatória.",
        "A URL da vaga é obrigatória.",
    ]


def test_invalid_url_reports_error() -> None:
    """Rejeita endereço sem protocolo e domínio válidos."""
    job = Job(
        title="Analista de Dados",
        company="Empresa Exemplo",
        url="example.com/jobs/456",
        source="Fonte Exemplo",
    )

    assert validate_job(job) == [
        "A URL da vaga deve usar HTTP ou HTTPS e possuir um domínio."
    ]


def test_dates_without_timezone_report_errors() -> None:
    """Rejeita datas que não informam seu fuso horário."""
    job = Job(
        title="Engenheira de Dados",
        company="Empresa Exemplo",
        url="https://example.com/jobs/789",
        source="Fonte Exemplo",
        published_at=datetime(2026, 8, 17, 9, 0),
        collected_at=datetime(2026, 8, 17, 10, 0),
    )

    assert validate_job(job) == [
        "A data de publicação deve possuir fuso horário.",
        "A data de coleta deve possuir fuso horário.",
    ]

