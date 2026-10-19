param([switch]$Foreground)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$bundledPython = Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
if (Test-Path -LiteralPath $bundledPython) { $serverPython = $bundledPython }
else { $serverPython = (Get-Command python -ErrorAction Stop).Source }
if ($Foreground) { & $serverPython -X utf8 server.py; exit $LASTEXITCODE }
try {
    $status = Invoke-RestMethod 'http://127.0.0.1:8765/api/status' -TimeoutSec 3
    if ($null -ne $status.ai_configured) { Write-Output 'Steer is already running: http://127.0.0.1:8765'; exit 0 }
} catch {}
$logDirectory = Join-Path $PSScriptRoot 'logs'
New-Item -ItemType Directory -Force -Path $logDirectory | Out-Null
$process = Start-Process -FilePath $serverPython -ArgumentList @('-X','utf8','server.py') -WorkingDirectory $PSScriptRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logDirectory 'server.log') -RedirectStandardError (Join-Path $logDirectory 'server-error.log') -PassThru
$process.Id | Set-Content -LiteralPath (Join-Path $logDirectory 'server.pid')
for ($attempt = 0; $attempt -lt 10; $attempt++) {
    Start-Sleep -Milliseconds 500
    try {
        $status = Invoke-RestMethod 'http://127.0.0.1:8765/api/status' -TimeoutSec 2
        if ($null -ne $status.ai_configured) { Write-Output 'Steer is running: http://127.0.0.1:8765'; exit 0 }
    } catch {}
}
throw 'Server did not become ready. Check logs/server-error.log.'
