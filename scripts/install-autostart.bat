@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

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
set TASK_NAME=PagoProveedoresColbeef
set START_BAT=%ROOT%\scripts\start-autostart.bat

if not exist "%START_BAT%" (
    echo [ERROR] No se encontro %START_BAT%
    exit /b 1
)

if not exist "%ROOT%\venv\Scripts\python.exe" (
    echo [ERROR] Ejecute primero scripts\setup.bat antes de registrar el auto-arranque.
    exit /b 1
)

echo ============================================
echo  AUTO-ARRANQUE - Pago Proveedores Colbeef
echo ============================================
echo.
echo Proyecto : %ROOT%
echo Script   : %START_BAT%
echo Tarea    : %TASK_NAME%
echo Trigger  : Al reiniciar Windows (~90 s despues del arranque)
echo.

schtasks /Create /TN "%TASK_NAME%" /TR "\"%START_BAT%\"" /SC ONSTART /DELAY 0001:30 /RL HIGHEST /F

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Tarea creada correctamente.
    echo.
    echo El programa iniciara solo tras cada reinicio del servidor:
    echo   - MySQL
    echo   - API en el puerto configurado en .env
    echo   - Sin abrir navegador
    echo   - Logs en logs\autostart.log y logs\api.log
    echo.
    echo Probar ahora manualmente:
    echo   schtasks /Run /TN "%TASK_NAME%"
    echo.
    echo Ver estado de la tarea:
    echo   schtasks /Query /TN "%TASK_NAME%" /V /FO LIST
    echo.
    echo Quitar auto-arranque:
    echo   scripts\uninstall-autostart.bat
) else (
    echo.
    echo [ERROR] No se pudo crear la tarea programada.
    exit /b 1
)

endlocal
