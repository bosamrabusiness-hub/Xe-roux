@echo off
setlocal
if "%BACKEND_PORT%"=="" set BACKEND_PORT=8000
if "%FRONTEND_PORT%"=="" set FRONTEND_PORT=5173
set "BASE_DIR=%~dp0"
if "%BASE_DIR:~-1%"=="\" set "BASE_DIR=%BASE_DIR:~0,-1%"
set "BACKEND_DIR=%BASE_DIR%\Xe-roux"
set "FRONTEND_DIR=%BACKEND_DIR%\clipx"

echo === Launching Xe-roux local environment ===

REM backend
start "XeRoux-Backend" /D "%BACKEND_DIR%" cmd /k "uvicorn app.main:app --reload --port %BACKEND_PORT%"

REM frontend (dependencies assumed installed)
start "XeRoux-Frontend" /D "%FRONTEND_DIR%" cmd /k "npm run dev -- --port %FRONTEND_PORT%"

REM open browser after 10s
timeout /t 10 /nobreak >nul
start "" http://localhost:%FRONTEND_PORT%

exit /b