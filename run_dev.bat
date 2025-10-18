@echo off
REM Relaunch self minimized unless already minimized
if "%1" NEQ "_min" (
    start "Launcher" /min cmd /c "%~f0" _min %*
    goto :eof
)
shift
setlocal
if "%BACKEND_PORT%"=="" set BACKEND_PORT=8000
if "%FRONTEND_PORT%"=="" set FRONTEND_PORT=5173
set "BASE_DIR=%~dp0"
if "%BASE_DIR:~-1%"=="\" set "BASE_DIR=%BASE_DIR:~0,-1%"
set "BACKEND_DIR=%BASE_DIR%\Xe-roux"
set "FRONTEND_DIR=%BACKEND_DIR%\clipx"

echo === Launching Xe-roux local environment ===

REM backend
start "XeRoux-Backend" /min /D "%BACKEND_DIR%" cmd /k "uvicorn app.main:app --reload --port %BACKEND_PORT%"

REM frontend (dependencies assumed installed)
start "XeRoux-Frontend" /min /D "%FRONTEND_DIR%" cmd /k "npm run dev -- --port %FRONTEND_PORT%"

REM open browser after 10s
timeout /t 10 /nobreak >nul
start "" http://localhost:%FRONTEND_PORT%

REM ===== Verify and install backend Python dependencies =====

echo Checking backend Python dependencies...
where pip >nul 2>&1 || (
    echo ERROR: Python/pip not found in PATH. Please install Python 3.10+ and ensure pip is available.
    pause & exit /b 1
)

REM Check if FastAPI is installed as a proxy for requirements
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo FastAPI (and probably other deps) not found. Installing backend requirements...
    pushd "%BACKEND_DIR%"
    pip install -r requirements.txt
    popd
) else (
    echo Backend requirements already satisfied.
)

REM ===== Verify and install frontend NPM dependencies =====

echo Checking frontend npm dependencies...
if not exist "%FRONTEND_DIR%\node_modules" (
    echo node_modules not found – installing frontend deps (npm ci)...
    pushd "%FRONTEND_DIR%"
    npm ci
    popd
) else (
    echo Frontend dependencies already installed.
)

exit /b