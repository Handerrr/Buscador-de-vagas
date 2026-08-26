"""Configurações da aplicação obtidas por variáveis de ambiente."""

import os
from dataclasses import dataclass
from urllib.parse import parse_qs, urlsplit

from job_monitor.filtering import JobFilterCriteria, parse_job_level


@dataclass(frozen=True)
class DatabaseSettings:
    """Configurações necessárias para conectar ao PostgreSQL."""

    host: str
    port: int
    name: str
    user: str
    password: str
    connection_url: str | None = None


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

    connection_url = os.getenv("DATABASE_URL")
    if connection_url:
        try:
            parsed_url = urlsplit(connection_url)
            port = parsed_url.port or 5432
        except ValueError as error:
            raise ValueError("DATABASE_URL possui uma porta inválida.") from error

        if parsed_url.scheme not in {"postgres", "postgresql"}:
            raise ValueError("DATABASE_URL deve usar o protocolo postgres ou postgresql.")
        if not parsed_url.hostname or not parsed_url.path.strip("/"):
            raise ValueError("DATABASE_URL deve informar servidor e banco de dados.")
        ssl_mode = parse_qs(parsed_url.query).get("sslmode", [""])[0]
        if ssl_mode not in {"require", "verify-ca", "verify-full"}:
            raise ValueError("DATABASE_URL pública deve exigir uma conexão SSL.")

        return DatabaseSettings(
            host=parsed_url.hostname,
            port=port,
            name=parsed_url.path.strip("/"),
            user=parsed_url.username or "",
            password=parsed_url.password or "",
            connection_url=connection_url,
        )

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
