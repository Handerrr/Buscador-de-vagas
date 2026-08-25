param(
    [string]$TaskName = "Monitor de Vagas",
    [int]$IntervalMinutes = 60
)

$ErrorActionPreference = "Stop"

if ($IntervalMinutes -lt 15) {
    throw "O intervalo mínimo permitido é de 15 minutos."
}

$runnerPath = Join-Path $PSScriptRoot "run_monitor.ps1"

if (-not (Test-Path -LiteralPath $runnerPath -PathType Leaf)) {
    throw "Script de execução não encontrado em: $runnerPath"
}

$powerShellArguments = "-NoProfile -NonInteractive -ExecutionPolicy Bypass -File `"$runnerPath`""
$action = New-ScheduledTaskAction `
    -Execute "powershell.exe" `
    -Argument $powerShellArguments

$trigger = New-ScheduledTaskTrigger `
    -Once `
    -At (Get-Date).AddMinutes(1) `
    -RepetitionInterval (New-TimeSpan -Minutes $IntervalMinutes)

$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Coleta vagas, salva novas no PostgreSQL e envia alertas pelo Telegram." `
    -Force

Write-Host "Tarefa '$TaskName' instalada com intervalo de $IntervalMinutes minutos."
