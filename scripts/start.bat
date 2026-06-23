@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

set ROOT=%~dp0..
cd /d "%ROOT%"

if not exist "venv\Scripts\activate.bat" (
    echo Ejecuta primero scripts\setup.bat
    exit /b 1
)

call scripts\stop.bat >nul 2>&1
call venv\Scripts\activate.bat
call scripts\start_mysql.bat

set PORT=8100
if exist "%ROOT%\.env" (
    for /f "usebackq tokens=1,* delims==" %%a in (`findstr /B /I "API_PORT=" "%ROOT%\.env"`) do (
        set PORT=%%b
    )
)

cd backend

echo Iniciando API en http://localhost:%PORT% ...
start "PagoProveedores-API" cmd /k "cd /d %ROOT%\backend && call %ROOT%\venv\Scripts\activate.bat && python -m uvicorn app.main:app --host 0.0.0.0 --port %PORT% --reload"

timeout /t 3 /nobreak >nul
start http://localhost:%PORT%/

endlocal
