"""Configurações da aplicação obtidas por variáveis de ambiente."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class DatabaseSettings:
    """Configurações necessárias para conectar ao PostgreSQL."""

    host: str
    port: int
    name: str
    user: str
    password: str


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

