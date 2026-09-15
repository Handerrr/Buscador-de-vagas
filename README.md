# Monitor Inteligente de Vagas

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

Aplicação Python que automatiza a busca por vagas de tecnologia. O sistema
consulta diferentes fontes, filtra e classifica oportunidades, evita duplicatas,
armazena os resultados e envia alertas pelo Telegram.

**[Acessar o dashboard público](https://monitor-vagas-handerr.streamlit.app/)**

## Como funciona

```text
Remote OK + Remotive
          │
          v
Coleta e padronização
          │
          v
Filtros para o Brasil + ranking por tecnologias
          │
          v
Validação + deduplicação
          │
          ├──> PostgreSQL / Neon ──> Dashboard Streamlit
          └──> Telegram Bot
```

O GitHub Actions executa a coleta a cada seis horas. Cada resposta é convertida
para um modelo único de vaga e comparada com cargos, níveis, localizações e
tecnologias configuráveis. Vagas novas são gravadas no PostgreSQL e notificadas;
duplicatas são descartadas por uma chave SHA-256 protegida também por uma
restrição `UNIQUE` no banco.

## Funcionalidades

- integração com as APIs públicas do Remote OK e Remotive;
- suporte a cargos em português e inglês;
- vagas brasileiras e remotas disponíveis para candidatos no Brasil;
- ranking determinístico por tecnologias preferidas;
- persistência e deduplicação no PostgreSQL;
- alertas com link da vaga pelo Telegram;
- dashboard com indicadores, gráficos, filtros, tabela e detalhes;
- execução automática com GitHub Actions ou worker Docker;
- modo de demonstração separado dos dados reais;
- testes unitários e de integração com Pytest.

## Tecnologias

| Área | Stack |
| --- | --- |
| Backend | Python 3.12 |
| Dashboard | Streamlit e Pandas |
| Banco | PostgreSQL, Psycopg 3 e Neon |
| Integrações | Remote OK, Remotive e Telegram Bot API |
| Automação | GitHub Actions e worker Python |
| Infraestrutura | Docker e Docker Compose |
| Testes | Pytest |

O projeto utiliza apenas serviços com opções gratuitas e não depende de APIs
pagas.

## Estrutura

```text
src/job_monitor/
├── dashboard/       # interface web
├── database/        # conexão, schema e consultas
├── notifier/        # notificações Telegram
├── scraper/         # integrações e utilitários HTTP
├── filtering.py     # filtros de relevância e localização
├── scoring.py       # pontuação por tecnologias
├── service.py       # validação, deduplicação e persistência
├── main.py          # execução de uma coleta
└── worker.py        # execução periódica
```

## Execução local

Requisitos: Python 3.11 ou superior, PostgreSQL e um bot do Telegram.

```powershell
git clone https://github.com/Handerrr/Buscador-de-vagas.git
Set-Location Buscador-de-vagas
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Preencha o `.env` com suas credenciais e preferências. Em seguida:

```powershell
$env:PYTHONPATH = "src"
python -m pytest
python -m job_monitor.main
.\scripts\run_dashboard.ps1
```

O dashboard local estará em `http://localhost:8501`.

Para testar a coleta sem enviar mensagens:

```powershell
python -m job_monitor.main --no-notifications
```

## Docker

O Compose inicia PostgreSQL, dashboard e worker periódico:

```powershell
docker compose up --build -d
docker compose ps
docker compose logs worker
```

Para encerrar sem remover o volume do banco:

```powershell
docker compose down
```

## Configuração

As opções estão documentadas em `.env.example`. As credenciais são:

- `DATABASE_URL` ou as variáveis individuais `DB_*`;
- `TELEGRAM_BOT_TOKEN`;
- `TELEGRAM_CHAT_ID`.

Os filtros usam `JOB_TITLES`, `JOB_LOCATIONS`, `JOB_LEVELS` e
`JOB_PREFERRED_KEYWORDS`. `DASHBOARD_DEMO_MODE=true` acrescenta exemplos
fictícios somente à interface; eles não são salvos nem notificados.

## Deploy

A versão pública utiliza:

- Streamlit Community Cloud para o dashboard;
- Neon para o PostgreSQL com SSL;
- GitHub Actions para as coletas;
- Telegram Bot API para os alertas.

Credenciais ficam em GitHub/Streamlit Secrets e nunca no repositório. O workflow
é habilitado pela variável `MONITOR_ENABLED=true` e também pode ser iniciado
manualmente em **Actions → Coletar vagas → Run workflow**.

## Segurança e testes

O `.env`, logs e secrets locais são ignorados pelo Git. Conexões públicas com o
PostgreSQL exigem SSL, a imagem Docker não recebe credenciais e o workflow possui
somente permissão de leitura sobre o código.

A suíte automatizada cobre APIs externas, configuração, filtros, ranking,
validação, deduplicação, banco, Telegram, worker, dashboard e arquivos de deploy.
