"""Testes de segurança e portabilidade dos scripts de automação."""

from pathlib import Path


PROJECT_DIRECTORY = Path(__file__).resolve().parents[1]
SCRIPTS_DIRECTORY = PROJECT_DIRECTORY / "scripts"


def test_automation_scripts_exist() -> None:
    """Mantém os dois scripts necessários sob controle de versão."""
    assert (SCRIPTS_DIRECTORY / "run_monitor.ps1").is_file()
    assert (SCRIPTS_DIRECTORY / "install_scheduled_task.ps1").is_file()


def test_scripts_do_not_contain_local_credentials_or_fixed_user_path() -> None:
    """Evita publicar credenciais ou caminhos exclusivos de uma máquina."""
    combined_content = "\n".join(
        script.read_text(encoding="utf-8")
        for script in SCRIPTS_DIRECTORY.glob("*.ps1")
    ).casefold()

    assert "telegram_bot_token=" not in combined_content
    assert "db_password=" not in combined_content
    assert "c:\\users\\" not in combined_content
