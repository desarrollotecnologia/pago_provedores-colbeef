@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

set ROOT=%~dp0..
cd /d "%ROOT%"

call "%ROOT%\scripts\_load_env.bat"

set PORT=8100
if defined API_PORT set PORT=%API_PORT%

echo ============================================
echo  Actualizando Pago Proveedores
echo ============================================

call scripts\stop.bat
call venv\Scripts\activate.bat
set PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
pip install -r requirements.txt -q

echo Reiniciando...
call scripts\start.bat
endlocal
