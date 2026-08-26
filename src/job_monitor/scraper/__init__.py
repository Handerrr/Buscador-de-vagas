"""Componentes responsáveis pela coleta de vagas."""

from job_monitor.scraper.remote_ok import RemoteOKError, fetch_remote_ok_jobs
from job_monitor.scraper.remotive import RemotiveError, fetch_remotive_jobs

__all__ = [
    "RemoteOKError",
    "RemotiveError",
    "fetch_remote_ok_jobs",
    "fetch_remotive_jobs",
]
