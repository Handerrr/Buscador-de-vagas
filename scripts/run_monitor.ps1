param(
    [switch]$NoNotifications
)

$ErrorActionPreference = "Stop"

$projectDirectory = Split-Path -Parent $PSScriptRoot
$pythonExecutable = Join-Path $projectDirectory ".venv\Scripts\python.exe"
$logDirectory = Join-Path $projectDirectory "logs"
$logFile = Join-Path $logDirectory ("monitor-{0}.log" -f (Get-Date -Format "yyyy-MM-dd"))

if (-not (Test-Path -LiteralPath $pythonExecutable -PathType Leaf)) {
    throw "Python do ambiente virtual não encontrado em: $pythonExecutable"
}

New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
Add-Content -LiteralPath $logFile -Value "`n[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Início da execução"

$previousPythonPath = $env:PYTHONPATH
$env:PYTHONPATH = Join-Path $projectDirectory "src"

try {
    $monitorArguments = @("-m", "job_monitor.main")

    if ($NoNotifications) {
        $monitorArguments += "--no-notifications"
    }

    & $pythonExecutable @monitorArguments 2>&1 |
        Tee-Object -FilePath $logFile -Append

    if ($LASTEXITCODE -ne 0) {
        throw "O monitor terminou com o código de saída $LASTEXITCODE."
    }
}
finally {
    $env:PYTHONPATH = $previousPythonPath
    Add-Content -LiteralPath $logFile -Value "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] Fim da execução"
}
