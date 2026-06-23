@echo off
chcp 65001 >nul
setlocal
set ROOT=%~dp0..
cd /d "%ROOT%\backend"
call "%ROOT%\venv\Scripts\activate.bat"
python -m app.seeds.verify_db
endlocal
