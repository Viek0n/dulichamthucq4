
$services = @(
    "user-service",
    "poi-service",
    "audio-service",
    "offline-package-service"
)

foreach ($service in $services) {
    $path = Join-Path $PSScriptRoot "backend\$service"

    Write-Host "`nSetting up $service..." -ForegroundColor Cyan

    # Create the virtual environment if it doesn't exist
    if (-not (Test-Path "$path\.venv\Scripts\python.exe")) {
        python -m venv "$path\.venv"
    }

    # Install this service's dependencies
    & "$path\.venv\Scripts\python.exe" -m pip install -r "$path\requirements.txt"

    if ($LASTEXITCODE -ne 0) {
        throw "Dependency installation failed for $service"
    }
}

Write-Host "`nAll services are set up!" -ForegroundColor Green
