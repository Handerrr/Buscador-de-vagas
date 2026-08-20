"""Geração de chaves para identificar vagas duplicadas."""

from hashlib import sha256

from job_monitor.models import Job


def _normalize_source_for_key(source: str) -> str:
    """Padroniza a fonte antes da geração da chave."""
    return " ".join(source.split()).casefold()


def generate_job_key(job: Job) -> str:
    """Gera uma chave determinística a partir da fonte e da URL da vaga."""
    normalized_source = _normalize_source_for_key(job.source)
    normalized_url = job.url.strip()
    identity = f"{normalized_source}\0{normalized_url}"

    return sha256(identity.encode("utf-8")).hexdigest()

