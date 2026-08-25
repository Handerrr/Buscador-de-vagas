"""Aplicação Streamlit do Monitor Inteligente de Vagas."""

import pandas as pd
import streamlit as st

from job_monitor.dashboard.data import (
    count_rows_by_field,
    filter_dashboard_rows,
    load_dashboard_rows,
    summarize_dashboard_rows,
)
from job_monitor.dashboard.demo_data import create_demo_rows, is_demo_mode_enabled


st.set_page_config(
    page_title="Monitor de Vagas",
    page_icon="🔎",
    layout="wide",
)

st.markdown(
    """
    <style>
        .block-container {padding-top: 2rem; padding-bottom: 3rem;}
        .hero {
            padding: 2rem;
            border-radius: 1.25rem;
            background: linear-gradient(135deg, #0f172a 0%, #123b55 55%, #0f766e 100%);
            color: white;
            margin-bottom: 1.5rem;
        }
        .hero h1 {margin: 0 0 .5rem 0; font-size: 2.35rem;}
        .hero p {margin: 0; color: #ccfbf1; font-size: 1.05rem;}
        [data-testid="stMetric"] {
            background: rgba(15, 118, 110, 0.08);
            border: 1px solid rgba(15, 118, 110, 0.2);
            padding: 1rem;
            border-radius: 1rem;
        }
    </style>
    <section class="hero">
        <h1>Monitor Inteligente de Vagas</h1>
        <p>Coleta automatizada, deduplicação e alertas para oportunidades relevantes.</p>
    </section>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=300)
def get_rows() -> list[dict[str, object]]:
    """Mantém os dados em cache por cinco minutos para poupar o banco."""
    database_rows = load_dashboard_rows()
    if is_demo_mode_enabled():
        return [*database_rows, *create_demo_rows()]
    return database_rows


try:
    rows = get_rows()
except Exception as error:
    st.error("Não foi possível carregar as vagas do PostgreSQL.")
    st.caption(f"Detalhe técnico: {type(error).__name__}")
    st.stop()

if not rows:
    st.info("Nenhuma vaga foi armazenada até o momento.")
    st.stop()

if is_demo_mode_enabled():
    st.warning(
        "Modo demonstração ativo: registros com fonte ‘Demonstração’ são exemplos "
        "fictícios e não representam vagas abertas."
    )

companies = sorted({str(row["Empresa"]) for row in rows})
sources = sorted({str(row["Fonte"]) for row in rows})
locations = sorted({str(row["Localização"]) for row in rows})

st.sidebar.header("Explorar vagas")
st.sidebar.caption("Os filtros atualizam todos os indicadores e gráficos.")
title_search = st.sidebar.text_input("Buscar cargo ou empresa")
selected_companies = st.sidebar.multiselect("Empresas", companies)
selected_sources = st.sidebar.multiselect("Fontes", sources)
selected_locations = st.sidebar.multiselect("Localizações", locations)

filtered_rows = filter_dashboard_rows(
    rows,
    search=title_search,
    companies=tuple(selected_companies),
    sources=tuple(selected_sources),
    locations=tuple(selected_locations),
)

summary = summarize_dashboard_rows(filtered_rows)
latest_collection_text = (
    summary.latest_collection.astimezone().strftime("%d/%m/%Y %H:%M")
    if summary.latest_collection is not None
    else "Sem dados"
)

total_column, companies_column, sources_column, update_column = st.columns(4)
total_column.metric("Vagas exibidas", summary.total_jobs)
companies_column.metric("Empresas", summary.total_companies)
sources_column.metric("Fontes", summary.total_sources)
update_column.metric("Última coleta", latest_collection_text)

overview_tab, jobs_tab, details_tab = st.tabs(
    ["Visão geral", "Todas as vagas", "Detalhes"],
)

with overview_tab:
    if not filtered_rows:
        st.info("Nenhuma vaga corresponde aos filtros escolhidos.")
    else:
        company_counts = count_rows_by_field(filtered_rows, "Empresa")
        location_counts = count_rows_by_field(filtered_rows, "Localização")
        company_chart, location_chart = st.columns(2)

        with company_chart:
            st.subheader("Vagas por empresa")
            st.bar_chart(
                pd.DataFrame.from_dict(
                    company_counts,
                    orient="index",
                    columns=["Vagas"],
                ),
                color="#0f766e",
            )

        with location_chart:
            st.subheader("Vagas por localização")
            st.bar_chart(
                pd.DataFrame.from_dict(
                    location_counts,
                    orient="index",
                    columns=["Vagas"],
                ),
                color="#2563eb",
            )

        st.success(
            "Banco conectado. Os dados desta página são atualizados automaticamente "
            "a cada cinco minutos."
        )

with jobs_tab:
    st.subheader("Vagas encontradas")
    table_rows = [
        {key: value for key, value in row.items() if key != "Descrição"}
        for row in filtered_rows
    ]
    st.dataframe(
        table_rows,
        width="stretch",
        hide_index=True,
        column_config={
            "Link": st.column_config.LinkColumn(
                "Link",
                display_text="Abrir vaga",
            ),
            "Publicada em": st.column_config.DatetimeColumn(
                "Publicada em",
                format="DD/MM/YYYY HH:mm",
            ),
            "Coletada em": st.column_config.DatetimeColumn(
                "Coletada em",
                format="DD/MM/YYYY HH:mm",
            ),
        },
    )

with details_tab:
    if not filtered_rows:
        st.info("Selecione filtros com resultados para consultar os detalhes.")
    else:
        selected_index = st.selectbox(
            "Escolha uma vaga",
            options=range(len(filtered_rows)),
            format_func=lambda index: (
                f"{filtered_rows[index]['Cargo']} — {filtered_rows[index]['Empresa']}"
            ),
        )
        selected_job = filtered_rows[selected_index]
        st.subheader(str(selected_job["Cargo"]))
        st.caption(
            f"{selected_job['Empresa']} · {selected_job['Localização']} · "
            f"{selected_job['Fonte']}"
        )
        st.write(selected_job["Descrição"])
        if selected_job["Link"]:
            st.link_button("Abrir vaga original", str(selected_job["Link"]))
        else:
            st.caption("Exemplo demonstrativo: não há link de candidatura.")
