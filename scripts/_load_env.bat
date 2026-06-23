@echo off
REM Carga variables de .env al entorno del script padre
setlocal EnableDelayedExpansion
set "ROOT=%~dp0.."
if not exist "%ROOT%\.env" exit /b 0
for /f "usebackq eol=# tokens=1,* delims==" %%a in ("%ROOT%\.env") do (
    set "line=%%a"
    if not "!line!"=="" (
        if not "%%a"=="" set "%%a=%%b"
    )
)
endlocal & (
    if defined DATABASE_URL set "DATABASE_URL=%DATABASE_URL%"
    if defined API_PORT set "API_PORT=%API_PORT%"
    if defined API_HOST set "API_HOST=%API_HOST%"
    if defined MYSQL_BIN set "MYSQL_BIN=%MYSQL_BIN%"
    if defined MYSQL_DATA set "MYSQL_DATA=%MYSQL_DATA%"
    if defined APP_URL set "APP_URL=%APP_URL%"
)
