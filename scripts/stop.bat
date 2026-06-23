@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

set ROOT=%~dp0..
set PORT=8100
if exist "%ROOT%\.env" (
    for /f "usebackq tokens=1,* delims==" %%a in (`findstr /B /I "API_PORT=" "%ROOT%\.env"`) do (
        set PORT=%%b
    )
)

echo Deteniendo Pago Proveedores en puerto %PORT% ...

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%PORT%" ^| findstr "LISTENING"') do (
    taskkill /PID %%a /F >nul 2>&1
)

echo Proceso detenido.

endlocal
