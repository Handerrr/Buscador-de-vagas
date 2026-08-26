"""Testes dos arquivos usados na publicação gratuita."""

from pathlib import Path


PROJECT_DIRECTORY = Path(__file__).resolve().parents[1]
WORKFLOW_FILE = PROJECT_DIRECTORY / ".github" / "workflows" / "monitor.yml"
ENTRYPOINT_FILE = PROJECT_DIRECTORY / "streamlit_app.py"


def test_public_deployment_files_exist() -> None:
    """Mantém entrypoint e automação pública sob controle de versão."""
    assert ENTRYPOINT_FILE.is_file()
    assert WORKFLOW_FILE.is_file()


def test_workflow_references_secrets_instead_of_credentials() -> None:
    """Evita gravar banco ou token do Telegram diretamente no workflow."""
    content = WORKFLOW_FILE.read_text(encoding="utf-8")

    assert "secrets.DATABASE_URL" in content
    assert "secrets.TELEGRAM_BOT_TOKEN" in content
    assert "secrets.TELEGRAM_CHAT_ID" in content
    assert "postgresql://" not in content
    assert "bot_token=" not in content.casefold()


def test_workflow_has_schedule_and_manual_execution() -> None:
    """Permite coletas automáticas e testes iniciados pelo usuário."""
    content = WORKFLOW_FILE.read_text(encoding="utf-8")

    assert 'cron: "17 */6 * * *"' in content
    assert "workflow_dispatch:" in content
    assert "timeout-minutes: 10" in content
    assert "vars.MONITOR_ENABLED == 'true'" in content
