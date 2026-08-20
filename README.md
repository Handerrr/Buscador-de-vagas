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
- `notifier`: envio futuro de notificações;
- `deduplication.py`: geração da chave única baseada em fonte e URL;
- `models.py`: representação padronizada dos dados de uma vaga;
- `normalizer.py`: padronização dos textos coletados;
- `service.py`: coordenação da normalização, validação e armazenamento;
- `validator.py`: verificação dos campos obrigatórios, URL e datas;
- `main.py`: ponto de entrada e coordenação dos componentes;
- `tests`: testes automatizados.

O modelo, a coleta pelo Remote OK, a normalização, a validação, a prevenção de
duplicatas e o armazenamento PostgreSQL já estão implementados. O componente de
notificação ainda existe apenas para estabelecer a organização inicial.

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
