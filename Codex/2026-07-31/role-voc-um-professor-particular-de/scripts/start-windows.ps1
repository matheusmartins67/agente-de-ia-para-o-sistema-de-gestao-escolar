param([ValidateRange(1024, 65535)][int]$PreferredPort = 8017)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot
if (-not (Test-Path '.env')) { Copy-Item '.env.example' '.env' }
$port = $PreferredPort
while (Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue) { $port++; if ($port -gt ($PreferredPort + 20)) { throw "No free port found between $PreferredPort and $($PreferredPort + 20)." } }
$envLines = Get-Content '.env'
if ($envLines -match '^HOST_PORT=') { $envLines = $envLines -replace '^HOST_PORT=.*', "HOST_PORT=$port" } else { $envLines += "HOST_PORT=$port" }
Set-Content '.env' $envLines -Encoding utf8
$logDir = Join-Path $projectRoot 'work\logs'; New-Item -ItemType Directory -Force $logDir | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$outLog = Join-Path $logDir "tutor-$stamp.out.log"
$errLog = Join-Path $logDir "tutor-$stamp.err.log"
# Avoid Start-Process: this Windows installation has conflicting PATH/Path entries.
cmd.exe /c "start `"`" /b py -3.13 -m app.standalone_server --port $port 1> `"$outLog`" 2> `"$errLog`""
for ($attempt = 1; $attempt -le 20; $attempt++) { Start-Sleep -Milliseconds 250; try { $health = Invoke-RestMethod "http://127.0.0.1:$port/api/v1/health" -TimeoutSec 2; if ($health.status -eq 'ok') { $listener = netstat -ano -p TCP | Select-String "127.0.0.1:$port\s+.*LISTENING" | Select-Object -First 1; $processId = if ($listener -match '\s+(\d+)\s*$') { $matches[1] } else { 'unknown' }; if ($processId -ne 'unknown') { Set-Content 'work\tutor-agent.pid' $processId -Encoding ascii }; Write-Host "School Management Assistant started: http://127.0.0.1:$port (PID $processId)"; $health | ConvertTo-Json -Compress; exit 0 } } catch { } }
throw 'The Tutor Agent did not pass its health check. See work\logs for details.'
