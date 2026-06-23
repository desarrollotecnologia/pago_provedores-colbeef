@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

set ROOT=%~dp0..
call "%ROOT%\scripts\_load_env.bat"

set PORT=8100
if defined API_PORT set PORT=%API_PORT%

set TASK_NAME=PagoProveedoresColbeef
set START_BAT=%ROOT%\scripts\start.bat

echo Creando tarea programada: %TASK_NAME%
echo Se ejecutara al iniciar sesion de Windows.

schtasks /Create /TN "%TASK_NAME%" /TR "\"%START_BAT%\"" /SC ONLOGON /RL HIGHEST /F

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Tarea creada. El sistema arrancara automaticamente al iniciar sesion.
    echo Para eliminar: schtasks /Delete /TN "%TASK_NAME%" /F
) else (
    echo.
    echo Error al crear la tarea. Ejecute este script como Administrador.
)

endlocal
