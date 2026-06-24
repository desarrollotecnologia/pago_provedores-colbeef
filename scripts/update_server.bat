@echo off
chcp 65001 >nul
setlocal

set ROOT=%~dp0..
cd /d "%ROOT%"

echo === Actualizar servidor Pago Proveedores ===

echo [1/4] git pull...
git pull
if errorlevel 1 (
    echo ERROR en git pull
    exit /b 1
)

echo [2/4] Crear/verificar tablas MySQL...
call venv\Scripts\activate.bat
cd backend
python -c "from app.seeds.setup_database import create_tables; create_tables()"
cd ..
if errorlevel 1 (
    echo ERROR creando tablas
    exit /b 1
)

echo [3/5] Compilar frontend...
call scripts\build_frontend.bat
if errorlevel 1 (
    echo ERROR compilando frontend
    exit /b 1
)

echo [4/5] Verificar build...
call scripts\verify_deploy.bat
if errorlevel 1 (
    exit /b 1
)

echo [5/5] Reiniciar servicio...
call scripts\restart.bat

echo.
echo Listo. Abra: http://192.168.20.205:8100
echo Si el navegador sigue en blanco: Ctrl+Shift+R para recargar sin cache.
endlocal
