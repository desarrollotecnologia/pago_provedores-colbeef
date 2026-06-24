@echo off
chcp 65001 >nul
setlocal

set ROOT=%~dp0..
cd /d "%ROOT%"

set SRC=
if exist "FIRMAS_COLBEEF_Mesa_de_trabajo_1.png" set SRC=FIRMAS_COLBEEF_Mesa_de_trabajo_1.png
if exist "email-banner-colbeef.png" set SRC=email-banner-colbeef.png

if "%SRC%"=="" (
  echo.
  echo Copie el banner Colbeef en la raiz del proyecto con uno de estos nombres:
  echo   FIRMAS_COLBEEF_Mesa_de_trabajo_1.png
  echo   email-banner-colbeef.png
  echo.
  echo Luego ejecute este script de nuevo.
  exit /b 1
)

if not exist "backend\app\static" mkdir "backend\app\static"
if not exist "frontend\public" mkdir "frontend\public"

copy /Y "%SRC%" "backend\app\static\email-banner-colbeef.png"
copy /Y "%SRC%" "frontend\public\email-banner-colbeef.png"

echo.
echo Banner instalado en:
echo   backend\app\static\email-banner-colbeef.png
echo   frontend\public\email-banner-colbeef.png
echo.
echo Reinicie el servidor: scripts\restart.bat
endlocal
