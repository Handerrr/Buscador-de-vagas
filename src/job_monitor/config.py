"""Configurações da aplicação obtidas por variáveis de ambiente."""

import os
from dataclasses import dataclass

from job_monitor.filtering import JobFilterCriteria, parse_job_level


@dataclass(frozen=True)
class DatabaseSettings:
    """Configurações necessárias para conectar ao PostgreSQL."""

    host: str
    port: int
    name: str
    user: str
    password: str


@dataclass(frozen=True)
class TelegramSettings:
    """Configurações necessárias para enviar mensagens pelo Telegram."""

    bot_token: str
    chat_id: str


def load_database_settings(*, load_env_file: bool = True) -> DatabaseSettings:
    """Carrega e valida as configurações de conexão com o banco de dados."""
    if load_env_file:
        from dotenv import load_dotenv

        load_dotenv()

    required_variables = ("DB_NAME", "DB_USER", "DB_PASSWORD")
    missing_variables = [
        variable for variable in required_variables if not os.getenv(variable)
    ]

    if missing_variables:
        variable_names = ", ".join(missing_variables)
        raise ValueError(f"Variáveis de ambiente obrigatórias ausentes: {variable_names}")

    port_text = os.getenv("DB_PORT", "5432")
    try:
        port = int(port_text)
    except ValueError as error:
        raise ValueError("DB_PORT deve ser um número inteiro.") from error

    return DatabaseSettings(
        host=os.getenv("DB_HOST", "localhost"),
        port=port,
        name=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
    )


def _split_setting(value: str | None) -> tuple[str, ...]:
    """Separa uma configuração composta por valores delimitados por vírgula."""
    if not value:
        return ()

    return tuple(item.strip() for item in value.split(",") if item.strip())


def load_job_filter_criteria(*, load_env_file: bool = True) -> JobFilterCriteria:
    """Carrega os critérios de relevância definidos no ambiente."""
    if load_env_file:
        from dotenv import load_dotenv

        load_dotenv()

    level_names = _split_setting(os.getenv("JOB_LEVELS"))
    return JobFilterCriteria(
        title_keywords=_split_setting(os.getenv("JOB_TITLES")),
        included_keywords=_split_setting(os.getenv("JOB_INCLUDED_KEYWORDS")),
        excluded_keywords=_split_setting(os.getenv("JOB_EXCLUDED_KEYWORDS")),
        locations=_split_setting(os.getenv("JOB_LOCATIONS")),
        levels=tuple(parse_job_level(level) for level in level_names),
    )


def load_job_scoring_keywords(*, load_env_file: bool = True) -> tuple[str, ...]:
    """Carrega os termos usados para pontuar e ordenar as vagas."""
    if load_env_file:
        from dotenv import load_dotenv

        load_dotenv()

    return _split_setting(os.getenv("JOB_PREFERRED_KEYWORDS"))


def load_telegram_settings(*, load_env_file: bool = True) -> TelegramSettings:
    """Carrega e valida as configurações do bot do Telegram."""
    if load_env_file:
        from dotenv import load_dotenv

        load_dotenv()

    required_variables = ("TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID")
    missing_variables = [
        variable for variable in required_variables if not os.getenv(variable)
    ]
    if missing_variables:
        variable_names = ", ".join(missing_variables)
        raise ValueError(
            f"Variáveis do Telegram obrigatórias ausentes: {variable_names}"
        )

    return TelegramSettings(
        bot_token=os.environ["TELEGRAM_BOT_TOKEN"],
        chat_id=os.environ["TELEGRAM_CHAT_ID"],
    )
