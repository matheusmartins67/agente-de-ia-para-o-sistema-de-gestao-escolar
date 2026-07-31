param(
    [ValidateRange(1024, 65535)]
    [int]$PreferredPort = 8017
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $projectRoot

if (-not (Test-Path '.env')) {
    Copy-Item '.env.example' '.env'
}

$port = $PreferredPort
while (Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue) {
    $port++
    if ($port -gt ($PreferredPort + 20)) {
        throw "No available port found between $PreferredPort and $($PreferredPort + 20)."
    }
}

$envLines = Get-Content '.env'
if ($envLines -match '^HOST_PORT=') {
    $envLines = $envLines -replace '^HOST_PORT=.*', "HOST_PORT=$port"
} else {
    $envLines += "HOST_PORT=$port"
}
Set-Content -Path '.env' -Value $envLines -Encoding utf8

docker info | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Docker Desktop is not running or its daemon is unavailable. Start Docker Desktop and run this script again."
}
docker compose up --build -d
if ($LASTEXITCODE -ne 0) {
    throw "Docker Compose could not start the Programming Tutor Agent. Review the Docker output above."
}
Write-Host "Programming Tutor Agent: http://127.0.0.1:$port"
Invoke-RestMethod "http://127.0.0.1:$port/api/v1/health"
