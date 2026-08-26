$ErrorActionPreference = "Continue"
$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = Join-Path $projectRoot "venv\Scripts\python.exe"
$logDirectory = Join-Path $projectRoot "logs"
$logFile = Join-Path $logDirectory "automation.log"

if (-not (Test-Path $python)) {
    throw "Virtual environment Python was not found at $python"
}

New-Item -ItemType Directory -Path $logDirectory -Force | Out-Null
Set-Location $projectRoot
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

while ($true) {
    Add-Content $logFile "[$(Get-Date -Format o)] Starting AutoMailing"
    & $python (Join-Path $projectRoot "app.py") *>> $logFile
    $exitCode = $LASTEXITCODE
    Add-Content $logFile "[$(Get-Date -Format o)] AutoMailing stopped with exit code $exitCode; restarting in 10 seconds"
    Start-Sleep -Seconds 10
}
