"""Testes da filtragem de vagas por relevância."""

from job_monitor import Job, JobFilterCriteria, filter_jobs, is_relevant


def _create_job(
    *,
    title: str = "Pessoa Desenvolvedora Python",
    description: str | None = "Construção de pipelines de dados.",
    location: str | None = "São Paulo, Brasil",
) -> Job:
    """Cria uma vaga com campos ajustáveis para os testes."""
    return Job(
        title=title,
        company="Empresa Exemplo",
        url="https://example.com/jobs/123",
        source="Fonte Exemplo",
        description=description,
        location=location,
    )


def test_empty_criteria_accept_every_job() -> None:
    """Mantém o comportamento atual quando nenhum critério é informado."""
    assert is_relevant(_create_job(), JobFilterCriteria()) is True


def test_included_keyword_matches_title_or_description() -> None:
    """Aceita a vaga quando uma palavra desejada aparece no texto."""
    criteria = JobFilterCriteria(included_keywords=("python", "sql"))

    assert is_relevant(_create_job(), criteria) is True
    assert is_relevant(_create_job(title="Designer", description="UX"), criteria) is False


def test_excluded_keyword_has_priority() -> None:
    """Rejeita uma vaga excluída mesmo quando ela atende à inclusão."""
    criteria = JobFilterCriteria(
        included_keywords=("python",),
        excluded_keywords=("senior",),
    )
    job = _create_job(title="Pessoa Desenvolvedora Python Sênior")

    assert is_relevant(job, criteria) is False


def test_search_ignores_case_and_accents() -> None:
    """Compara textos sem diferenciar caixa ou acentuação."""
    criteria = JobFilterCriteria(
        included_keywords=("ANALISE",),
        locations=("sao paulo",),
    )
    job = _create_job(description="Análise de dados em Python.")

    assert is_relevant(job, criteria) is True


def test_location_must_match_when_configured() -> None:
    """Rejeita vagas fora das localidades aceitas."""
    criteria = JobFilterCriteria(locations=("Brasil", "Worldwide"))

    assert is_relevant(_create_job(location="Lisboa, Portugal"), criteria) is False


def test_filter_jobs_preserves_only_relevant_jobs() -> None:
    """Mantém a ordem original ao produzir a lista filtrada."""
    python_job = _create_job()
    design_job = _create_job(title="Product Designer", description="Design de produto")
    criteria = JobFilterCriteria(included_keywords=("python",))

    assert filter_jobs([python_job, design_job], criteria) == [python_job]

