$ErrorActionPreference = "Stop"

$projectDirectory = Split-Path -Parent $PSScriptRoot
$pythonExecutable = Join-Path $projectDirectory ".venv\Scripts\python.exe"
$dashboardFile = Join-Path $projectDirectory "src\job_monitor\dashboard\app.py"

if (-not (Test-Path -LiteralPath $pythonExecutable -PathType Leaf)) {
    throw "Python do ambiente virtual não encontrado em: $pythonExecutable"
}

$previousPythonPath = $env:PYTHONPATH
$env:PYTHONPATH = Join-Path $projectDirectory "src"

try {
    & $pythonExecutable -m streamlit run $dashboardFile
}
finally {
    $env:PYTHONPATH = $previousPythonPath
}
