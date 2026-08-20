"""Componentes responsáveis pela coleta de vagas."""

from job_monitor.scraper.remote_ok import RemoteOKError, fetch_remote_ok_jobs

__all__ = ["RemoteOKError", "fetch_remote_ok_jobs"]
