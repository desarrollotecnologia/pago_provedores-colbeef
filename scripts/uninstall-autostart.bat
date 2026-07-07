@echo off
chcp 65001 >nul
setlocal

set TASK_NAME=PagoProveedoresColbeef

net session >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Ejecute este script como Administrador.
    pause
    exit /b 1
)

echo Eliminando tarea programada: %TASK_NAME%
schtasks /Delete /TN "%TASK_NAME%" /F

if %ERRORLEVEL% EQU 0 (
    echo Tarea eliminada. El sistema ya no arrancara solo al reiniciar.
) else (
    echo No se encontro la tarea o hubo un error al eliminarla.
)

endlocal
