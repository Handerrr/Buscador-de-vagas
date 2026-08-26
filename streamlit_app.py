"""Ponto de entrada usado pelo Streamlit Community Cloud."""

import os
import sys
from pathlib import Path

import streamlit as st


SOURCE_DIRECTORY = Path(__file__).resolve().parent / "src"
sys.path.insert(0, str(SOURCE_DIRECTORY))

try:
    for secret_name in ("DATABASE_URL", "DASHBOARD_DEMO_MODE"):
        if secret_name in st.secrets and not os.getenv(secret_name):
            os.environ[secret_name] = str(st.secrets[secret_name])
except FileNotFoundError:
    pass

from job_monitor.dashboard import app  # noqa: E402,F401
