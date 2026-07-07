@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

set ROOT=%~dp0..
cd /d "%ROOT%"

if not exist "logs" mkdir "logs"

set "LOG=%ROOT%\logs\watchdog-autostart.log"
call :log "=== Watchdog Pago Proveedores ==="

set PORT=8100
if exist "%ROOT%\.env" (
    for /f "usebackq tokens=1,* delims==" %%a in (`findstr /B /I "API_PORT=" "%ROOT%\.env"`) do (
        set PORT=%%b
    )
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%PORT%" ^| findstr "LISTENING"') do (
    call :log "API activa en puerto %PORT% (PID %%a)."
    exit /b 0
)

call :log "API no esta activa en puerto %PORT%. Ejecutando start-autostart.bat..."
call "%ROOT%\scripts\start-autostart.bat"
set RESULT=%ERRORLEVEL%

if "%RESULT%"=="0" (
    call :log "Arranque automatico completado."
) else (
    call :log "ERROR: start-autostart.bat termino con codigo %RESULT%."
)

exit /b %RESULT%

:log
echo [%DATE% %TIME%] %~1>> "%LOG%"
exit /b 0
