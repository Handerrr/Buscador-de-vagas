"""Dados fictícios usados exclusivamente para apresentar o painel."""

import os
from datetime import UTC, datetime, timedelta
from typing import Any


DEMO_JOBS = (
    ("Estágio em Análise de Dados", "Empresa Aurora", "São Paulo, Brasil", "Python, SQL e Power BI"),
    ("Desenvolvedor Python Júnior", "Nuvem Tech", "Remoto, Brasil", "APIs Python, PostgreSQL e testes"),
    ("Analista de BI Pleno", "Dados do Sul", "Curitiba, Brasil", "Dashboards, ETL e Power BI"),
    ("Engenheira de Dados Pleno", "Horizonte Digital", "Remoto, Brasil", "Pipelines, Python, SQL e AWS"),
    ("Cientista de Dados Júnior", "Verde Analytics", "Belo Horizonte, Brasil", "Machine Learning e experimentação"),
    ("Desenvolvedor Backend Pleno", "Conecta Sistemas", "Recife, Brasil", "Python, APIs e PostgreSQL"),
    ("Analista de Sistemas Júnior", "Ponte Software", "Fortaleza, Brasil", "Requisitos, SQL e integrações"),
    ("Engenheiro DevOps Sênior", "Órbita Cloud", "Remoto, Brasil", "Docker, CI/CD, AWS e observabilidade"),
    ("Analista de Qualidade Pleno", "Produto Vivo", "Florianópolis, Brasil", "Automação de testes e APIs"),
    ("Desenvolvedora Frontend Júnior", "Estúdio Web", "Porto Alegre, Brasil", "TypeScript, React e testes"),
    ("Engenheiro de Machine Learning Pleno", "IA Aplicada", "Remoto, Brasil", "Python, MLOps e Azure"),
    ("Analista de Segurança da Informação", "Escudo Digital", "Brasília, Brasil", "Cloud, monitoramento e resposta a incidentes"),
)


def is_demo_mode_enabled() -> bool:
    """Informa se o painel deve acrescentar exemplos fictícios identificados."""
    return os.getenv("DASHBOARD_DEMO_MODE", "false").strip().casefold() in {
        "1",
        "true",
        "yes",
        "sim",
    }


def create_demo_rows(*, reference_time: datetime | None = None) -> list[dict[str, Any]]:
    """Cria exemplos determinísticos sem persistir ou notificar qualquer vaga."""
    base_time = reference_time or datetime.now(UTC)
    return [
        {
            "Cargo": title,
            "Empresa": company,
            "Localização": location,
            "Fonte": "Demonstração",
            "Publicada em": base_time - timedelta(days=index + 1),
            "Coletada em": base_time - timedelta(hours=index * 3),
            "Link": None,
            "Descrição": (
                "Exemplo fictício criado para demonstrar a interface. "
                f"Tecnologias ilustrativas: {technologies}."
            ),
        }
        for index, (title, company, location, technologies) in enumerate(DEMO_JOBS)
    ]
