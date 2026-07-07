@echo off
chcp 65001 >nul
setlocal

set ROOT=%~dp0..
cd /d "%ROOT%"

call scripts\install-autostart.bat
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%

call scripts\install-watchdog.bat
if %ERRORLEVEL% NEQ 0 exit /b %ERRORLEVEL%

echo.
echo Auto-arranque y watchdog instalados correctamente.
endlocal
