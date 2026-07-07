@echo off
chcp 65001 >nul
setlocal

net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Ejecute este script como Administrador.
    echo         Clic derecho -^> Ejecutar como administrador
    echo.
    pause
    exit /b 1
)

set ROOT=%~dp0..
set TASK_NAME=PagoProveedoresColbeefWatchdog
set WATCHDOG_BAT=%ROOT%\scripts\watchdog-autostart.bat

if not exist "%WATCHDOG_BAT%" (
    echo [ERROR] No se encontro %WATCHDOG_BAT%
    exit /b 1
)

if not exist "%ROOT%\venv\Scripts\python.exe" (
    echo [ERROR] Ejecute primero scripts\setup.bat antes de registrar el watchdog.
    exit /b 1
)

echo ============================================
echo  WATCHDOG - Pago Proveedores Colbeef
echo ============================================
echo.
echo Proyecto : %ROOT%
echo Script   : %WATCHDOG_BAT%
echo Tarea    : %TASK_NAME%
echo Trigger  : Cada 5 minutos
echo Usuario  : SYSTEM
echo.

schtasks /Create /TN "%TASK_NAME%" /TR "\"%WATCHDOG_BAT%\"" /SC MINUTE /MO 5 /RU SYSTEM /RL HIGHEST /F

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Tarea watchdog creada correctamente.
    echo.
    echo Si el programa no esta iniciado, el watchdog lo arrancara automaticamente.
    echo Logs:
    echo   logs\watchdog-autostart.log
    echo   logs\autostart.log
    echo   logs\api.log
    echo.
    echo Probar ahora manualmente:
    echo   schtasks /Run /TN "%TASK_NAME%"
    echo.
) else (
    echo.
    echo [ERROR] No se pudo crear la tarea watchdog.
    exit /b 1
)

endlocal
