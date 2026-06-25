@echo off
chcp 65001 >nul
setlocal
set ROOT=%~dp0..
cd /d "%ROOT%\backend"
if exist "%ROOT%\venv\Scripts\activate.bat" call "%ROOT%\venv\Scripts\activate.bat"
python -m app.seeds.validate_excel_db %*
set EXIT_CODE=%ERRORLEVEL%
endlocal & exit /b %EXIT_CODE%
