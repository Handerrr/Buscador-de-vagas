# Monitor Inteligente de Vagas

Projeto educacional em Python para coletar, organizar e identificar vagas de
emprego relevantes, evitando registros duplicados.

O desenvolvimento será incremental. Decisões como fontes das vagas, banco de
dados e serviço de notificações ainda serão avaliadas antes da implementação.

## Fluxo planejado

```text
Coleta
  -> Normalização
  -> Validação
  -> Detecção de duplicatas
  -> Armazenamento
  -> Filtragem ou classificação
  -> Notificação
```

## Estrutura atual

```text
.
|-- src/
|   `-- job_monitor/
|       |-- scraper/
|       |   `-- remote_ok.py
|       |-- database/
|       |   |-- connection.py
|       |   |-- repository.py
|       |   `-- schema.py
|       |-- notifier/
|       |-- config.py
|       |-- __init__.py
|       |-- deduplication.py
|       |-- models.py
|       |-- normalizer.py
|       |-- service.py
|       |-- validator.py
|       `-- main.py
|-- tests/
|-- .env.example
|-- .gitignore
|-- pyproject.toml
|-- requirements.txt
`-- README.md
```

Cada diretório possui uma responsabilidade:

- `scraper`: coleta de vagas pela API pública do Remote OK;
- `database`: conexão e estrutura PostgreSQL para armazenamento das vagas;
- `config.py`: leitura segura das configurações do ambiente;
- `notifier`: formatação e envio de notificações pelo Telegram;
- `deduplication.py`: geração da chave única baseada em fonte e URL;
- `models.py`: representação padronizada dos dados de uma vaga;
- `normalizer.py`: padronização dos textos coletados;
- `service.py`: coordenação da normalização, validação e armazenamento;
- `validator.py`: verificação dos campos obrigatórios, URL e datas;
- `main.py`: ponto de entrada e coordenação dos componentes;
- `tests`: testes automatizados.

O modelo, a coleta pelo Remote OK, a normalização, a validação, a prevenção de
duplicatas, o armazenamento PostgreSQL e as notificações pelo Telegram já estão
implementados.

## Fonte de vagas

O primeiro coletor utiliza o feed JSON público e gratuito do Remote OK. A fonte
deve ser mencionada como `Remote OK`, e cada vaga deve manter o link original
recebido da API. O projeto não usa o logotipo da plataforma.

## Preparação do ambiente

É recomendado utilizar Python 3.11 ou uma versão mais recente.

Crie um ambiente virtual:

```powershell
python -m venv .venv
```

Ative o ambiente no PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
python -m pip install -r requirements.txt
```

Crie a configuração local a partir do modelo:

```powershell
Copy-Item .env.example .env
```

Edite o arquivo `.env` com os dados da sua instalação PostgreSQL. Esse arquivo
é local, está ignorado pelo Git e nunca deve ser publicado.

Execute os testes:

```powershell
python -m pytest
```

Execute o monitor com os filtros e o limite padrão (`python`, `data` e 50
vagas):

```powershell
$env:PYTHONPATH = "src"
python -m job_monitor.main
```

Para escolher tags e limite:

```powershell
python -m job_monitor.main --tags python data --limit 20
```

Para aplicar critérios locais de relevância:

```powershell
python -m job_monitor.main `
    --tags python data `
    --include-keywords python sql "data engineer" `
    --exclude-keywords senior lead `
    --locations worldwide brazil brasil `
    --limit 20
```

Por padrão, os critérios são carregados do `.env`. O projeto está configurado
com 15 famílias de cargos comuns em tecnologia e dados no Brasil, incluindo
aliases em português e inglês, os níveis estágio, júnior, pleno e sênior, e as
localizações `Brasil` e `Brazil`. Argumentos informados no terminal substituem
a configuração correspondente naquela execução.

As vagas relevantes também são ordenadas por tecnologias preferidas. Cada termo
encontrado no título soma 3 pontos; quando aparece somente na descrição, soma 1
ponto. A maior pontuação é processada primeiro, antes da aplicação do limite.

Os termos padrão são Python, SQL, Power BI, PostgreSQL, ETL, Machine Learning,
Inteligência Artificial, Engenharia de Dados, AWS e Azure. Eles podem ser
substituídos em uma execução com `--preferred-keywords`.

As palavras de inclusão e exclusão são procuradas no título e na descrição. As
comparações ignoram maiúsculas, minúsculas e acentos. Sem esses argumentos,
todas as vagas recebidas da API são consideradas relevantes.

A execução coleta as vagas do Remote OK, normaliza, valida e armazena as novas
vagas no PostgreSQL. Cada vaga realmente inserida gera uma mensagem no Telegram;
duplicatas e vagas inválidas não geram alertas. Ao final, o terminal também exibe
quantas notificações foram enviadas ou falharam.

Para executar temporariamente sem enviar mensagens:

```powershell
python -m job_monitor.main --no-notifications
```

Uma falha momentânea do Telegram não interrompe a coleta nem desfaz a vaga já
salva. A falha aparece no resumo da execução.

## Execução automática no Windows

O script `scripts/run_monitor.ps1` localiza o projeto a partir da própria pasta,
usa o Python instalado em `.venv`, configura `src` no `PYTHONPATH` e executa o
monitor. Ele pode ser testado manualmente sem notificações com:

```powershell
.\scripts\run_monitor.ps1 -NoNotifications
```

O script `scripts/install_scheduled_task.ps1` registra uma tarefa gratuita no
Agendador de Tarefas do Windows. Por padrão, ela começa aproximadamente um minuto
depois da instalação e se repete a cada 60 minutos:

```powershell
.\scripts\install_scheduled_task.ps1
```

Para escolher outro intervalo, respeitando o mínimo de 15 minutos:

```powershell
.\scripts\install_scheduled_task.ps1 -IntervalMinutes 30
```

A opção `-StartWhenAvailable` permite que uma execução perdida comece quando o
computador voltar a estar disponível. A opção `IgnoreNew` impede duas execuções
simultâneas caso uma coleta ainda esteja em andamento.

Cada execução grava sua saída em `logs/monitor-AAAA-MM-DD.log`. O arquivo é
acumulado durante o dia e permite verificar o resultado das execuções em segundo
plano. A pasta `logs` é local e está ignorada pelo Git.

Para conferir o estado da tarefa:

```powershell
Get-ScheduledTask -TaskName "Monitor de Vagas"
```

Para removê-la futuramente:

```powershell
Unregister-ScheduledTask -TaskName "Monitor de Vagas"
```

## Painel web local

O painel gratuito em Streamlit consulta as vagas armazenadas no PostgreSQL e
oferece indicadores, busca por cargo ou empresa e filtros por empresa, fonte e
localização. A visão geral apresenta gráficos por empresa e localização; as
outras abas exibem a tabela completa e os detalhes da vaga selecionada.

Para apresentações, `DASHBOARD_DEMO_MODE=true` acrescenta 12 exemplos fictícios
claramente marcados com a fonte `Demonstração`. Esses registros existem apenas
na memória do painel: não são gravados no PostgreSQL, não possuem link de
candidatura e nunca são enviados ao Telegram. Use `false` para exibir somente
oportunidades reais.
Para iniciá-lo no Windows:

```powershell
.\scripts\run_dashboard.ps1
```

Depois, acesse `http://localhost:8501`. O endereço `localhost` restringe o acesso
ao próprio computador. O painel mantém os resultados em cache por cinco minutos
para evitar consultas repetidas ao banco.

## Ambiente com Docker

O `Dockerfile` descreve a imagem Python, enquanto `compose.yaml` conecta três
serviços: `web`, com Streamlit; `worker`, com a coleta periódica e o Telegram; e
`database`, com PostgreSQL. O banco utiliza um volume chamado
`postgres_data_v18`, portanto seus dados sobrevivem à recriação dos contêineres.

O worker executa uma coleta assim que inicia e aguarda 60 minutos antes da
próxima. O intervalo pode ser alterado em `MONITOR_INTERVAL_MINUTES`, respeitando
o mínimo de 15 minutos.

Use apenas um agendador por vez. Ao manter o serviço `worker` ativo, desabilite a
tarefa equivalente do Agendador do Windows para evitar duas coletas independentes:

```powershell
Disable-ScheduledTask -TaskName "Monitor de Vagas"
```

Para voltar ao agendamento do Windows, pare o ambiente Docker e reabilite a
tarefa:

```powershell
docker compose down
Enable-ScheduledTask -TaskName "Monitor de Vagas"
```

Para construir e iniciar o ambiente:

```powershell
docker compose up --build -d
```

Para consultar o estado e os logs:

```powershell
docker compose ps
docker compose logs web
docker compose logs worker
```

Para parar os serviços sem apagar o banco:

```powershell
docker compose down
```

O arquivo `.dockerignore` impede que credenciais do `.env`, ambiente virtual,
histórico do Git e logs locais sejam enviados para a construção da imagem.

## Publicação gratuita

A arquitetura pública recomendada usa Streamlit Community Cloud para o painel,
Neon para o PostgreSQL e GitHub Actions para executar a coleta. O Docker continua
disponível para desenvolvimento local e para demonstrar a portabilidade.

O banco gerenciado fornece uma `DATABASE_URL`. A aplicação aceita essa variável
com prioridade sobre `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` e `DB_PASSWORD`.
Por segurança, a URL pública deve conter `sslmode=require`, `verify-ca` ou
`verify-full`.

No Streamlit Community Cloud, selecione o repositório, a branch `main`, Python
3.12 e o arquivo `streamlit_app.py`. Cadastre apenas estes valores em **Secrets**:

```toml
DATABASE_URL = "postgresql://usuario:senha@servidor/banco?sslmode=require"
DASHBOARD_DEMO_MODE = "true"
```

O arquivo `.streamlit/secrets.toml.example` serve como modelo. O arquivo real
`secrets.toml` está ignorado pelo Git.

No GitHub, acesse **Settings > Secrets and variables > Actions**. Cadastre como
**Secrets**, que são confidenciais:

- `DATABASE_URL`;
- `TELEGRAM_BOT_TOKEN`;
- `TELEGRAM_CHAT_ID`.

Cadastre como **Variables**, que controlam os filtros e não são credenciais:

- `MONITOR_ENABLED`, inicialmente `false` e alterado para `true` após configurar
  todos os Secrets;
- `JOB_TITLES`;
- `JOB_INCLUDED_KEYWORDS`;
- `JOB_EXCLUDED_KEYWORDS`;
- `JOB_LOCATIONS`;
- `JOB_LEVELS`;
- `JOB_PREFERRED_KEYWORDS`.

Os valores de filtro podem ser copiados de `.env.example`. O workflow valida os
itens obrigatórios antes da coleta, pode ser acionado manualmente e também roda
a cada seis horas pelo arquivo `.github/workflows/monitor.yml`.

Para executar também o teste de integração com o PostgreSQL local:

```powershell
$env:RUN_DATABASE_INTEGRATION = "1"
python -m pytest
Remove-Item Env:RUN_DATABASE_INTEGRATION
```

Esse teste confirma a inserção e a prevenção de duplicatas dentro de uma
transação que é desfeita ao final, sem manter dados fictícios no banco.

As operações atuais do repositório permitem salvar uma vaga, buscá-la por sua
chave de duplicidade e listar as vagas mais recentes com um limite configurável.

## Segurança

O arquivo `.env` está ignorado pelo Git e deverá conter apenas configurações
locais. Quando variáveis forem necessárias, seus nomes serão documentados em
`.env.example`, sempre sem tokens, senhas ou outras credenciais reais.
