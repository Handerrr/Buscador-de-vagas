# Monitor Inteligente de Vagas

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-dashboard-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

Sistema automatizado que coleta vagas de tecnologia, identifica oportunidades
compatíveis com um perfil configurável, elimina duplicatas e envia alertas pelo
Telegram. Os resultados ficam armazenados em PostgreSQL e disponíveis em um
dashboard público desenvolvido com Streamlit.

**[Acessar o dashboard online](https://monitor-vagas-handerr.streamlit.app/)**

> O dashboard utiliza dados reais coletados das APIs e pode acrescentar registros
> claramente identificados como `Demonstração` para manter o portfólio navegável
> quando há poucas vagas compatíveis no momento.

## O problema resolvido

Procurar vagas em diferentes plataformas exige consultas repetitivas e gera
resultados duplicados ou pouco relevantes. Este projeto transforma esse processo
em um pipeline automatizado:

1. consulta APIs públicas de vagas;
2. converte respostas diferentes para um modelo de dados único;
3. filtra cargos, níveis e regiões aceitas para candidatos no Brasil;
4. classifica oportunidades por tecnologias preferidas;
5. evita inserir a mesma vaga mais de uma vez;
6. persiste os resultados e alerta o usuário pelo Telegram;
7. apresenta indicadores e detalhes em uma aplicação web.

## Competências demonstradas

- integração com APIs REST externas e tratamento de respostas JSON;
- arquitetura modular e separação de responsabilidades em Python;
- modelagem e persistência de dados com PostgreSQL;
- deduplicação determinística com SHA-256 e restrição `UNIQUE` no banco;
- filtros configuráveis, normalização textual e ranking por relevância;
- automação periódica e execução manual com GitHub Actions;
- notificações por meio da API oficial do Telegram;
- dashboard interativo e publicação com Streamlit;
- conteinerização de aplicação, worker e banco com Docker Compose;
- testes unitários e de integração com `pytest`;
- gerenciamento seguro de configurações com variáveis de ambiente e secrets.

## Tecnologias

| Área | Tecnologias |
| --- | --- |
| Linguagem | Python 3.12 |
| Interface web | Streamlit, Pandas |
| Banco de dados | PostgreSQL, Psycopg 3, Neon |
| Fontes de vagas | APIs públicas do Remote OK e Remotive |
| Notificações | Telegram Bot API |
| Automação | GitHub Actions, worker Python, Agendador de Tarefas do Windows |
| Infraestrutura | Docker, Docker Compose, Streamlit Community Cloud |
| Qualidade | Pytest, testes unitários e teste de integração transacional |
| Configuração | python-dotenv, GitHub Secrets e Streamlit Secrets |

Todos os serviços usados na implantação pública possuem opção gratuita e o
projeto não depende de APIs pagas.

## Arquitetura e fluxo

```text
Remote OK API ─┐
               ├─> Coleta e padronização ─> Filtros ─> Ranking
Remotive API ──┘                                      │
                                                      v
                                             Validação e deduplicação
                                                      │
                                      ┌───────────────┴───────────────┐
                                      v                               v
                              PostgreSQL / Neon                Telegram Bot
                                      │
                                      v
                              Dashboard Streamlit
```

Na implantação pública, o GitHub Actions executa o monitor a cada seis horas.
O dashboard consulta o mesmo banco Neon e mantém os resultados em cache por
cinco minutos para reduzir acessos desnecessários.

## Principais decisões técnicas

### Modelo único para múltiplas fontes

Remote OK e Remotive usam formatos diferentes. Cada coletor converte sua resposta
para o modelo interno `Job`, permitindo que filtros, ranking, persistência e
notificações funcionem sem conhecer detalhes da plataforma de origem.

### Deduplicação em duas camadas

A identidade é calculada com SHA-256 a partir de `fonte + URL normalizada`. A
coluna `job_key` também possui uma restrição `UNIQUE` no PostgreSQL. Assim, a
aplicação possui uma verificação determinística e o banco garante a integridade
mesmo diante de execuções concorrentes.

### Filtros voltados ao Brasil

Os critérios aceitam 15 famílias de cargos com aliases em português e inglês,
níveis de estágio a sênior e localizações brasileiras. Vagas remotas marcadas
como `Worldwide`, `Americas`, `Latin America` ou `South America` também são
consideradas quando permitem candidatura a partir do Brasil.

### Ranking explicável

O ranking não depende de uma API de inteligência artificial. Cada tecnologia
preferida encontrada no título soma três pontos; quando encontrada somente na
descrição, soma um ponto. A regra é simples, auditável e pode ser ajustada pelo
arquivo de configuração.

### Falhas isoladas de notificação

Uma vaga é persistida antes do envio ao Telegram. Se o serviço de mensagens
estiver indisponível, a coleta continua e o erro aparece no resumo, sem desfazer
o registro que já foi salvo.

## Dashboard

O painel oferece:

- indicadores de vagas, empresas, fontes e última coleta;
- filtros por cargo, empresa, fonte e localização;
- gráficos de distribuição por empresa e região;
- tabela com links para as vagas originais;
- aba de detalhes com descrição completa;
- modo demonstrativo separado dos dados reais.

Registros com fonte `Demonstração` são criados somente na memória do dashboard.
Eles não são persistidos, notificados ou apresentados como oportunidades reais.

## Estrutura do projeto

```text
.
├── .github/workflows/monitor.yml       # automação em produção
├── scripts/                            # execução local e Agendador do Windows
├── src/job_monitor/
│   ├── dashboard/                      # interface e preparação dos dados
│   ├── database/                       # conexão, schema e repositório
│   ├── notifier/                       # integração com Telegram
│   ├── scraper/                        # coletores Remote OK e Remotive
│   ├── config.py                       # variáveis de ambiente
│   ├── filtering.py                    # filtros e localização
│   ├── scoring.py                      # pontuação e ordenação
│   ├── deduplication.py                # chave determinística
│   ├── service.py                      # processamento de cada vaga
│   ├── main.py                         # orquestração de uma coleta
│   └── worker.py                       # execução periódica em contêiner
├── tests/                              # testes unitários e de integração
├── compose.yaml                        # web, worker e PostgreSQL
├── Dockerfile
├── streamlit_app.py                    # entrada do Streamlit Cloud
└── requirements.txt
```

## Executando localmente

### Pré-requisitos

- Python 3.11 ou superior;
- PostgreSQL, local ou gerenciado;
- bot do Telegram para receber notificações.

Clone o repositório e prepare o ambiente:

```powershell
git clone https://github.com/Handerrr/Buscador-de-vagas.git
Set-Location Buscador-de-vagas
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Preencha o `.env` com suas próprias credenciais. O arquivo está no `.gitignore`
e nunca deve ser enviado ao repositório.

Execute os testes:

```powershell
$env:PYTHONPATH = "src"
python -m pytest
```

Execute uma coleta sem notificações:

```powershell
python -m job_monitor.main --no-notifications
```

Execute normalmente, salvando as vagas e notificando pelo Telegram:

```powershell
python -m job_monitor.main
```

Inicie o dashboard:

```powershell
.\scripts\run_dashboard.ps1
```

Acesse `http://localhost:8501`.

## Executando com Docker

O ambiente Docker cria três serviços:

- `web`: dashboard Streamlit;
- `worker`: coleta periódica e notificações;
- `database`: PostgreSQL com volume persistente.

Depois de preencher o `.env`, execute:

```powershell
docker compose up --build -d
docker compose ps
docker compose logs worker
```

Para encerrar sem apagar os dados:

```powershell
docker compose down
```

Use somente um agendador por vez. Se o `worker` estiver ativo no Docker, não
mantenha simultaneamente a tarefa do Agendador do Windows ou o workflow de
produção apontando para o mesmo destino de notificações.

## Configurações principais

O arquivo `.env.example` documenta todas as opções. As mais importantes são:

| Variável | Finalidade | Sensível |
| --- | --- | --- |
| `DATABASE_URL` | conexão SSL com PostgreSQL gerenciado | sim |
| `TELEGRAM_BOT_TOKEN` | autenticação do bot | sim |
| `TELEGRAM_CHAT_ID` | destinatário dos alertas | sim |
| `JOB_TITLES` | cargos aceitos | não |
| `JOB_LOCATIONS` | localizações aceitas | não |
| `JOB_LEVELS` | níveis de senioridade | não |
| `JOB_PREFERRED_KEYWORDS` | tecnologias usadas no ranking | não |
| `DASHBOARD_DEMO_MODE` | habilita exemplos visuais no painel | não |
| `MONITOR_INTERVAL_MINUTES` | intervalo do worker Docker | não |

## Testes e qualidade

A suíte cobre:

- interpretação das APIs Remote OK e Remotive;
- normalização e validação das vagas;
- filtros de texto, senioridade e localização;
- pontuação e ordenação por relevância;
- criação da chave de deduplicação;
- operações do repositório PostgreSQL;
- formatação e falhas da notificação Telegram;
- orquestração, worker, dashboard e arquivos de deploy.

O teste de integração com PostgreSQL roda dentro de uma transação revertida ao
final, evitando manter dados fictícios:

```powershell
$env:RUN_DATABASE_INTEGRATION = "1"
python -m pytest
Remove-Item Env:RUN_DATABASE_INTEGRATION
```

## Implantação pública gratuita

A versão online utiliza:

- **Streamlit Community Cloud** para o dashboard;
- **Neon** para PostgreSQL gerenciado com SSL;
- **GitHub Actions** para coleta agendada;
- **Telegram Bot API** para alertas.

Credenciais são cadastradas como secrets nas respectivas plataformas. Filtros
não sensíveis ficam em GitHub Actions Variables. O workflow também pode ser
acionado manualmente em **Actions → Coletar vagas → Run workflow**.

A variável `MONITOR_ENABLED` deve conter somente `true` para permitir as
execuções. O agendamento está definido para quatro ciclos diários, respeitando a
recomendação de uso da API pública da Remotive.

## Segurança

- `.env`, logs, ambientes virtuais e secrets locais são ignorados pelo Git;
- conexões públicas PostgreSQL exigem `sslmode=require`, `verify-ca` ou
  `verify-full`;
- imagens Docker não recebem `.env` nem o histórico do repositório;
- o workflow possui apenas permissão de leitura sobre o código;
- nenhuma credencial é incluída no código-fonte ou no `.env.example`.

## Próximas evoluções

- paginação e histórico de execuções no dashboard;
- acompanhamento do status de candidatura;
- métricas de aderência por tecnologia;
- novas fontes brasileiras que ofereçam APIs públicas compatíveis;
- pipeline separado de CI para executar testes a cada alteração.

---

Projeto desenvolvido para demonstrar integração de sistemas, automação,
persistência de dados, testes e publicação de uma aplicação Python completa.
