$ErrorActionPreference = "Stop"
$taskName = "AutoMailingAutomation"

Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue
Write-Output "Removed $taskName."
