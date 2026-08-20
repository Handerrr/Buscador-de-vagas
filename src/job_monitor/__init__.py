"""Monitor inteligente de vagas."""

from job_monitor.config import DatabaseSettings, load_database_settings
from job_monitor.deduplication import generate_job_key
from job_monitor.filtering import JobFilterCriteria, filter_jobs, is_relevant
from job_monitor.models import Job
from job_monitor.normalizer import normalize_job
from job_monitor.service import (
    JobProcessingResult,
    JobProcessingStatus,
    process_job,
)
from job_monitor.validator import validate_job

__all__ = [
    "DatabaseSettings",
    "Job",
    "JobFilterCriteria",
    "JobProcessingResult",
    "JobProcessingStatus",
    "generate_job_key",
    "filter_jobs",
    "is_relevant",
    "load_database_settings",
    "normalize_job",
    "process_job",
    "validate_job",
]
__version__ = "0.1.0"
