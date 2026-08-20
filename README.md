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
|       |-- database/
|       |-- notifier/
|       |-- __init__.py
|       |-- deduplication.py
|       |-- models.py
|       |-- normalizer.py
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

- `scraper`: coleta de vagas em fontes externas;
- `database`: armazenamento, consultas e prevenção de duplicatas;
- `notifier`: envio futuro de notificações;
- `deduplication.py`: geração da chave única baseada em fonte e URL;
- `models.py`: representação padronizada dos dados de uma vaga;
- `normalizer.py`: padronização dos textos coletados;
- `validator.py`: verificação dos campos obrigatórios, URL e datas;
- `main.py`: ponto de entrada e coordenação dos componentes;
- `tests`: testes automatizados.

O modelo inicial de vaga, a normalização, a validação e a geração da chave para
detectar duplicatas já estão implementados. Os componentes de coleta,
armazenamento e notificação ainda existem apenas para estabelecer a organização
inicial.

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

Execute os testes:

```powershell
python -m pytest
```

## Segurança

O arquivo `.env` está ignorado pelo Git e deverá conter apenas configurações
locais. Quando variáveis forem necessárias, seus nomes serão documentados em
`.env.example`, sempre sem tokens, senhas ou outras credenciais reais.
