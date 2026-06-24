@echo off
chcp 65001 >nul
setlocal

set ROOT=%~dp0..
cd /d "%ROOT%"

set ERR=0

echo === Verificar deploy ===

if not exist "frontend\dist\assets" (
    echo ERROR: No existe frontend\dist. Ejecute scripts\build_frontend.bat
    set ERR=1
    goto :end
)

findstr /M /C:"Está seguro" "frontend\dist\assets\*.js" >nul 2>&1
if not errorlevel 1 (
    echo ERROR: El frontend compilado aun usa confirm del navegador.
    set ERR=1
)

findstr /M /C:"confirm-dialog" "frontend\dist\assets\*.js" >nul 2>&1
if errorlevel 1 (
    echo ERROR: No se encontro el modal confirm-dialog en el build.
    set ERR=1
)

call venv\Scripts\activate.bat 2>nul
cd backend
python -c "from app.version import APP_VERSION, EMAIL_TEMPLATE_VERSION; assert APP_VERSION=='1.2.0'; assert EMAIL_TEMPLATE_VERSION=='2'; print('Backend OK:', APP_VERSION, 'correo v'+EMAIL_TEMPLATE_VERSION)"
if errorlevel 1 set ERR=1
cd ..

:end
if %ERR%==1 (
    echo.
    echo Verificacion FALLIDA. No despliegue hasta corregir.
    exit /b 1
)

echo.
echo Verificacion OK — listo para reiniciar servidor.
endlocal
