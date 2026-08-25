"""Testes da pontuação e ordenação das vagas."""

from job_monitor import Job, rank_jobs, score_job


def _create_job(
    title: str,
    description: str | None = None,
) -> Job:
    """Cria uma vaga ajustável para os testes de pontuação."""
    return Job(
        title=title,
        company="Empresa Exemplo",
        url=f"https://example.com/jobs/{title}",
        source="Fonte Exemplo",
        description=description,
    )


def test_title_match_is_worth_three_points() -> None:
    """Prioriza termos encontrados diretamente no título."""
    job = _create_job("Python Developer")

    result = score_job(job, ("python",))

    assert result.score == 3
    assert result.matched_keywords == ("python",)


def test_description_match_is_worth_one_point() -> None:
    """Pontua menos quando o termo aparece somente na descrição."""
    job = _create_job("Data Analyst", "Experiência com PostgreSQL.")

    result = score_job(job, ("postgresql",))

    assert result.score == 1
    assert result.matched_keywords == ("postgresql",)


def test_keyword_is_counted_only_once() -> None:
    """Ignora repetição e diferenças de caixa ou acento nos critérios."""
    job = _create_job("Engenheiro de Inteligência Artificial")

    result = score_job(
        job,
        ("inteligência artificial", "INTELIGENCIA ARTIFICIAL"),
    )

    assert result.score == 3
    assert result.matched_keywords == ("inteligência artificial",)


def test_job_without_matches_has_zero_score() -> None:
    """Mantém pontuação zero quando nenhum termo é encontrado."""
    job = _create_job("Product Designer", "Design de interfaces.")

    assert score_job(job, ("python", "sql")).score == 0


def test_rank_jobs_orders_by_score_and_preserves_ties() -> None:
    """Ordena por pontuação sem alterar a ordem de vagas empatadas."""
    first_tied_job = _create_job("Data Analyst", "Uso de SQL.")
    second_tied_job = _create_job("BI Analyst", "Uso de SQL.")
    highest_job = _create_job("Python Developer", "Uso de SQL.")

    ranked_jobs = rank_jobs(
        [first_tied_job, second_tied_job, highest_job],
        ("python", "sql"),
    )

    assert [item.job for item in ranked_jobs] == [
        highest_job,
        first_tied_job,
        second_tied_job,
    ]
    assert [item.score for item in ranked_jobs] == [4, 1, 1]

