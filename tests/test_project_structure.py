"""Testes básicos da estrutura inicial do projeto."""

import job_monitor


def test_package_has_initial_version() -> None:
    """Confirma que o pacote principal pode ser importado."""
    assert job_monitor.__version__ == "0.1.0"

