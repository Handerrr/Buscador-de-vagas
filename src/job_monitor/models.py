"""Modelos de dados utilizados pelo monitor de vagas."""

from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class Job:
    """Representa uma vaga de emprego coletada de uma fonte externa."""

    title: str
    company: str
    url: str
    source: str
    location: str | None = None
    description: str | None = None
    published_at: datetime | None = None
    collected_at: datetime = field(default_factory=lambda: datetime.now(UTC))

