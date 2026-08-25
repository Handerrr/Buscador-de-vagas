"""Leitura e preparação dos dados exibidos no painel."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from job_monitor.config import load_database_settings
from job_monitor.database import connect_database, initialize_database
from job_monitor.database.repository import list_jobs
from job_monitor.models import Job


@dataclass(frozen=True)
class DashboardSummary:
    """Indicadores calculados a partir das vagas atualmente filtradas."""

    total_jobs: int
    total_companies: int
    total_sources: int
    latest_collection: datetime | None


def job_to_dashboard_row(job: Job) -> dict[str, Any]:
    """Converte uma vaga em uma linha amigável para o Streamlit."""
    return {
        "Cargo": job.title,
        "Empresa": job.company,
        "Localização": job.location or "Não informada",
        "Fonte": job.source,
        "Publicada em": job.published_at,
        "Coletada em": job.collected_at,
        "Link": job.url,
        "Descrição": job.description or "Descrição não informada.",
    }


def filter_dashboard_rows(
    rows: list[dict[str, Any]],
    *,
    search: str = "",
    companies: tuple[str, ...] = (),
    sources: tuple[str, ...] = (),
    locations: tuple[str, ...] = (),
) -> list[dict[str, Any]]:
    """Aplica os filtros escolhidos sem alterar a lista original."""
    normalized_search = search.strip().casefold()

    return [
        row
        for row in rows
        if (
            not normalized_search
            or normalized_search in str(row["Cargo"]).casefold()
            or normalized_search in str(row["Empresa"]).casefold()
        )
        and (not companies or row["Empresa"] in companies)
        and (not sources or row["Fonte"] in sources)
        and (not locations or row["Localização"] in locations)
    ]


def summarize_dashboard_rows(rows: list[dict[str, Any]]) -> DashboardSummary:
    """Calcula os indicadores apresentados no topo do painel."""
    collection_dates = [
        row["Coletada em"] for row in rows if isinstance(row["Coletada em"], datetime)
    ]
    return DashboardSummary(
        total_jobs=len(rows),
        total_companies=len({row["Empresa"] for row in rows}),
        total_sources=len({row["Fonte"] for row in rows}),
        latest_collection=max(collection_dates, default=None),
    )


def count_rows_by_field(
    rows: list[dict[str, Any]],
    field: str,
) -> dict[str, int]:
    """Agrupa vagas por um campo para alimentar gráficos."""
    counts: dict[str, int] = {}
    for row in rows:
        value = str(row[field])
        counts[value] = counts.get(value, 0) + 1

    return dict(sorted(counts.items(), key=lambda item: (-item[1], item[0])))


def load_dashboard_rows(*, limit: int = 500) -> list[dict[str, Any]]:
    """Busca vagas no PostgreSQL e sempre encerra a conexão utilizada."""
    connection = connect_database(load_database_settings())

    try:
        initialize_database(connection)
        return [job_to_dashboard_row(job) for job in list_jobs(connection, limit=limit)]
    finally:
        connection.close()
