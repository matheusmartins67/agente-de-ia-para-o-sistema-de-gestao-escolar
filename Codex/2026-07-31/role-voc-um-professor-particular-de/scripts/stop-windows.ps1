$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$pidFile = Join-Path $projectRoot 'work\tutor-agent.pid'
$processId = if (Test-Path $pidFile) { Get-Content $pidFile -Raw } else { '' }
if ($processId -notmatch '^\d+$') {
    $port = (Get-Content (Join-Path $projectRoot '.env') | Where-Object { $_ -match '^HOST_PORT=' } | Select-Object -First 1) -replace '^HOST_PORT=', ''
    $listener = netstat -ano -p TCP | Select-String "127.0.0.1:$port\s+.*LISTENING" | Select-Object -First 1
    if ($listener -match '\s+(\d+)\s*$') { $processId = $matches[1] }
}
if ($processId -notmatch '^\d+$') { Write-Host 'No running Tutor Agent was found.'; exit 0 }
$process = Get-Process -Id $processId -ErrorAction SilentlyContinue
if ($process) { Stop-Process -Id $processId -Force; Write-Host "Tutor Agent stopped (PID $processId)." }
Remove-Item $pidFile -Force
