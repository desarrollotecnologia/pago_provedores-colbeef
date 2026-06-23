@echo off
chcp 65001 >nul
setlocal

set ROOT=%~dp0..
cd /d "%ROOT%\frontend"

if not exist "node_modules" (
    echo Instalando dependencias del frontend...
    call npm install
    if %ERRORLEVEL% NEQ 0 exit /b 1
)

echo Compilando frontend...
call npm run build
if %ERRORLEVEL% NEQ 0 exit /b 1

echo.
echo Frontend compilado en frontend\dist
endlocal
