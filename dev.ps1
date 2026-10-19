
# Stop immediately if a required file or folder is missing
$ErrorActionPreference = "Stop"

# Find the project root from this script's location
$ProjectRoot = $PSScriptRoot

$FrontendPath = Join-Path $ProjectRoot "frontend"
$BackendPath  = Join-Path $ProjectRoot "backend"

# Check that both projects exist
if (-not (Test-Path (Join-Path $FrontendPath "package.json"))) {
    throw "Cannot find frontend/package.json"
}

if (-not (Test-Path (Join-Path $BackendPath "app/main.py"))) {
    throw "Cannot find backend/app/main.py"
}

if (-not (Test-Path (Join-Path $BackendPath ".venv/Scripts/python.exe"))) {
    throw "Backend virtual environment not found. Create backend/.venv first."
}

# Start the React frontend in a new PowerShell window
$FrontendCommand = "Set-Location '$FrontendPath'; npm run dev"

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command", $FrontendCommand
)

# Start the FastAPI backend in another PowerShell window
$BackendCommand = "Set-Location '$BackendPath'; .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000"

Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command", $BackendCommand
)

Write-Host "Frontend and backend startup commands launched." -ForegroundColor Green
Write-Host "Frontend: http://localhost:5173"
Write-Host "Backend:  http://localhost:8000"
Write-Host "API docs: http://localhost:8000/docs"
