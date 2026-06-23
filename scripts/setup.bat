@echo off
chcp 65001 >nul
setlocal

set ROOT=%~dp0..
cd /d "%ROOT%"

echo ============================================
echo  PAGO PROVEEDORES - Setup Fase 1
echo ============================================
echo.

if not exist ".env" (
    echo [INFO] Creando .env desde .env.example...
    copy /Y ".env.example" ".env" >nul
    echo [AVISO] Edita el archivo .env con tu contraseña de MySQL antes de continuar.
    echo.
)

if not exist "venv" (
    echo [1/4] Creando entorno virtual...
    python -m venv venv
) else (
    echo [1/4] Entorno virtual ya existe.
)

echo [2/4] Instalando dependencias...
call venv\Scripts\activate.bat
set PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
pip install -r requirements.txt -q

echo [3/4] Verificando MySQL...
call scripts\start_mysql.bat

echo [4/4] Ejecutando seed e importacion Excel...
cd backend
python -m app.seeds.run_seed %*

echo.
echo [5/5] Compilando frontend...
cd /d "%ROOT%"
call scripts\build_frontend.bat

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] La inicializacion fallo. Verifica que MySQL este corriendo
    echo         y que DATABASE_URL en .env sea correcta.
    exit /b 1
)

echo.
echo Setup completado. Para iniciar el API:
echo   scripts\start.bat
endlocal
