"""Monitor inteligente de vagas."""

from job_monitor.config import (
    DatabaseSettings,
    load_database_settings,
    load_job_filter_criteria,
)
from job_monitor.deduplication import generate_job_key
from job_monitor.filtering import (
    JobFilterCriteria,
    JobLevel,
    filter_jobs,
    infer_job_level,
    is_relevant,
    parse_job_level,
)
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
    "JobLevel",
    "JobProcessingResult",
    "JobProcessingStatus",
    "generate_job_key",
    "filter_jobs",
    "infer_job_level",
    "is_relevant",
    "load_database_settings",
    "load_job_filter_criteria",
    "normalize_job",
    "process_job",
    "parse_job_level",
    "validate_job",
]
__version__ = "0.1.0"
