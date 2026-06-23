@echo off
chcp 65001 >nul
setlocal

if defined MYSQL_BIN (
    set "BIN=%MYSQL_BIN%"
) else (
    set "BIN=C:\Program Files\MySQL\MySQL Server 8.4\bin"
)

if defined MYSQL_DATA (
    set "DATA=%MYSQL_DATA%"
) else (
    set "DATA=C:\ProgramData\MySQL\MySQL Server 8.4\Data"
)

if exist "%BIN%\mysqld.exe" (
    tasklist /FI "IMAGENAME eq mysqld.exe" 2>nul | find /I "mysqld.exe" >nul
    if errorlevel 1 (
        echo Iniciando MySQL...
        start "" /B "%BIN%\mysqld.exe" --datadir="%DATA%"
        timeout /t 4 /nobreak >nul
    ) else (
        echo MySQL ya esta en ejecucion.
    )
) else (
    echo [AVISO] MySQL no encontrado en ruta predeterminada.
    echo         Asegurate de que el servicio MySQL este activo.
)

endlocal
