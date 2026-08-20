"""Testes da geração de chaves para vagas."""

from job_monitor import Job, generate_job_key


def _create_job(**changes: str) -> Job:
    """Cria uma vaga padrão, permitindo alterar campos em cada teste."""
    data = {
        "title": "Pessoa Desenvolvedora Python",
        "company": "Empresa Exemplo",
        "url": "https://example.com/jobs/123",
        "source": "Fonte Exemplo",
    }
    data.update(changes)
    return Job(**data)


def test_same_source_and_url_generate_same_key() -> None:
    """Identifica como duplicadas vagas com a mesma fonte e URL."""
    first_job = _create_job(title="Pessoa Desenvolvedora Python")
    second_job = _create_job(title="Desenvolvedor Python Sênior")

    assert generate_job_key(first_job) == generate_job_key(second_job)


def test_key_ignores_source_formatting_differences() -> None:
    """Ignora capitalização e espaços excedentes no nome da fonte."""
    first_job = _create_job(source="Fonte Exemplo")
    second_job = _create_job(source="  FONTE   exemplo  ")

    assert generate_job_key(first_job) == generate_job_key(second_job)


def test_different_url_generates_different_key() -> None:
    """Mantém separadas vagas que possuem URLs diferentes."""
    first_job = _create_job(url="https://example.com/jobs/123")
    second_job = _create_job(url="https://example.com/jobs/456")

    assert generate_job_key(first_job) != generate_job_key(second_job)


def test_different_source_generates_different_key() -> None:
    """Mantém separadas publicações provenientes de fontes diferentes."""
    first_job = _create_job(source="Fonte A")
    second_job = _create_job(source="Fonte B")

    assert generate_job_key(first_job) != generate_job_key(second_job)


def test_generated_key_is_sha256_hexadecimal() -> None:
    """Produz uma chave SHA-256 hexadecimal com tamanho fixo."""
    key = generate_job_key(_create_job())

    assert len(key) == 64
    assert all(character in "0123456789abcdef" for character in key)

