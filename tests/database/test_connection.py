"""Testes da criação de conexões com o PostgreSQL."""

import sys
from types import SimpleNamespace
from typing import Any

import pytest

from job_monitor import DatabaseSettings
from job_monitor.database import connect_database


def test_connect_database_passes_settings_to_driver(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Repassa as configurações ao driver sem acessar um banco real."""
    received_arguments: dict[str, Any] = {}
    fake_connection = object()

    def fake_connect(**arguments: Any) -> object:
        received_arguments.update(arguments)
        return fake_connection

    fake_psycopg = SimpleNamespace(connect=fake_connect)
    monkeypatch.setitem(sys.modules, "psycopg", fake_psycopg)
    settings = DatabaseSettings(
        host="localhost",
        port=5432,
        name="job_monitor_test",
        user="test_user",
        password="test_password",
    )

    connection = connect_database(settings)

    assert connection is fake_connection
    assert received_arguments == {
        "host": "localhost",
        "port": 5432,
        "dbname": "job_monitor_test",
        "user": "test_user",
        "password": "test_password",
    }

