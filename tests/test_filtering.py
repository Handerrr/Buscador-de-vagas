"""Testes da filtragem de vagas por relevância."""

from job_monitor import (
    Job,
    JobFilterCriteria,
    JobLevel,
    filter_jobs,
    infer_job_level,
    is_relevant,
    parse_job_level,
)


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


def test_brazil_filter_accepts_remote_regions_that_include_brazil() -> None:
    """Aceita regiões globais ou americanas onde candidatos do Brasil podem atuar."""
    criteria = JobFilterCriteria(locations=("Brasil", "Brazil"))

    assert is_relevant(_create_job(location="Worldwide"), criteria) is True
    assert is_relevant(_create_job(location="Anywhere"), criteria) is True
    assert is_relevant(_create_job(location="Americas, Europe, Israel"), criteria) is True
    assert is_relevant(_create_job(location="Latin America"), criteria) is True
    assert is_relevant(_create_job(location="South America"), criteria) is True


def test_brazil_filter_rejects_incompatible_remote_region() -> None:
    """Não trata uma vaga limitada a outro país ou continente como brasileira."""
    criteria = JobFilterCriteria(locations=("Brasil", "Brazil"))

    assert is_relevant(_create_job(location="United States only"), criteria) is False
    assert is_relevant(_create_job(location="Europe"), criteria) is False


def test_filter_jobs_preserves_only_relevant_jobs() -> None:
    """Mantém a ordem original ao produzir a lista filtrada."""
    python_job = _create_job()
    design_job = _create_job(title="Product Designer", description="Design de produto")
    criteria = JobFilterCriteria(included_keywords=("python",))

    assert filter_jobs([python_job, design_job], criteria) == [python_job]


def test_title_keywords_match_only_job_title() -> None:
    """Não aceita um cargo apenas porque ele é citado na descrição."""
    criteria = JobFilterCriteria(title_keywords=("analista de dados",))
    job = _create_job(
        title="Assistente Administrativo",
        description="Contato diário com o analista de dados.",
    )

    assert is_relevant(job, criteria) is False


def test_infer_job_level_in_portuguese_and_english() -> None:
    """Reconhece aliases de senioridade usados nos dois idiomas."""
    assert infer_job_level(_create_job(title="Analista de Dados Júnior")) is JobLevel.JUNIOR
    assert infer_job_level(_create_job(title="Senior Data Engineer")) is JobLevel.SENIOR
    assert parse_job_level("Estagiário") is JobLevel.INTERNSHIP
    assert parse_job_level("Pleno") is JobLevel.MID_LEVEL


def test_configured_levels_reject_other_identified_level() -> None:
    """Rejeita um nível identificado que não esteja entre os aceitos."""
    criteria = JobFilterCriteria(levels=(JobLevel.JUNIOR, JobLevel.MID_LEVEL))

    assert is_relevant(_create_job(title="Senior Data Engineer"), criteria) is False
    assert is_relevant(_create_job(title="Data Engineer"), criteria) is True
