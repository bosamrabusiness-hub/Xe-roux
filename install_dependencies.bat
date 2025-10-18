@echo off
REM =============================================================
REM  install_dependencies.bat
REM  ------------------------
REM  Stand-alone helper script to install ALL project libraries
REM  (backend Python packages + frontend Node packages).
REM  Just double-click this file once after cloning the repo.
REM =============================================================

REM Determine directories
set "BASE_DIR=%~dp0"
if "%BASE_DIR:~-1%"=="\" set "BASE_DIR=%BASE_DIR:~0,-1%"
set "BACKEND_DIR=%BASE_DIR%\Xe-roux"
set "FRONTEND_DIR=%BACKEND_DIR%\clipx"

echo =============================================================
echo  Installing backend Python dependencies
echo  Backend dir: %BACKEND_DIR%
echo =============================================================

REM Ensure python and pip are available
where python >nul 2>&1 || (
    echo ERROR: Python not found in PATH. Please install Python 3.10+ and ensure it is added to PATH.
    pause & exit /b 1
)

REM Upgrade pip using python -m pip to avoid launcher issues
python -m pip install --upgrade pip || (
    echo ERROR: Failed to upgrade pip. Aborting.
    pause & exit /b 1
)

if not exist "%BACKEND_DIR%\requirements.txt" (
    echo ERROR: requirements.txt not found in %BACKEND_DIR% . Aborting.
    pause & exit /b 1
)

pushd "%BACKEND_DIR%"
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install backend requirements.
    popd
    pause & exit /b 1
)
popd

echo.
echo =============================================================
echo  Installing frontend Node dependencies
echo  Frontend dir: %FRONTEND_DIR%
echo =============================================================

if not exist "%FRONTEND_DIR%\package.json" (
    echo ERROR: package.json not found in %FRONTEND_DIR% . Aborting.
    pause & exit /b 1
)

pushd "%FRONTEND_DIR%"
REM Prefer reproducible install; fall back to npm install
call npm ci || call npm install
if errorlevel 1 (
    echo ERROR: Failed to install frontend dependencies.
    popd
    pause & exit /b 1
)
popd

echo.
echo =============================================================
echo  ✅  All dependencies installed successfully!
echo =============================================================

pause