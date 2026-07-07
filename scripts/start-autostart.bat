@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

set ROOT=%~dp0..
cd /d "%ROOT%"

if not exist "logs" mkdir "logs"

set "LOG=%ROOT%\logs\autostart.log"
call :log "=== Auto-arranque Pago Proveedores ==="

if not exist "venv\Scripts\python.exe" (
    call :log "ERROR: No existe venv. Ejecute scripts\setup.bat"
    exit /b 1
)

if not exist "frontend\dist\index.html" (
    call :log "AVISO: frontend\dist no encontrado. La API arrancara pero la web puede fallar."
)

set PORT=8100
if exist "%ROOT%\.env" (
    for /f "usebackq tokens=1,* delims==" %%a in (`findstr /B /I "API_PORT=" "%ROOT%\.env"`) do (
        set PORT=%%b
    )
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%PORT%" ^| findstr "LISTENING"') do (
    call :log "API ya activa en puerto %PORT% (PID %%a). Nada que hacer."
    exit /b 0
)

call :log "Iniciando MySQL..."
call scripts\start_mysql.bat >> "%LOG%" 2>&1

set /a WAIT_COUNT=0
:wait_mysql
netstat -ano | findstr ":3306" | findstr "LISTENING" >nul
if not errorlevel 1 goto mysql_ready
set /a WAIT_COUNT+=1
if !WAIT_COUNT! GEQ 30 (
    call :log "AVISO: MySQL no respondio en 60 s. Se intentara iniciar la API igualmente."
    goto start_api
)
powershell -NoProfile -Command "Start-Sleep -Seconds 2" >nul 2>&1
goto wait_mysql

:mysql_ready
call :log "MySQL listo."

:start_api
call :log "Iniciando API en puerto %PORT% (sin navegador, modo produccion)..."

start "PagoProveedores-API" /MIN cmd /c "cd /d %ROOT%\backend && %ROOT%\venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port %PORT% >> %ROOT%\logs\api.log 2>&1"

powershell -NoProfile -Command "Start-Sleep -Seconds 5" >nul 2>&1

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%PORT%" ^| findstr "LISTENING"') do (
    call :log "API activa en puerto %PORT% (PID %%a)."
    exit /b 0
)

call :log "ERROR: La API no quedo escuchando en el puerto %PORT%. Revise logs\api.log"
exit /b 1

:log
echo [%DATE% %TIME%] %~1>> "%LOG%"
exit /b 0
