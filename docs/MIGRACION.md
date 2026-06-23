# Migración a otro servidor

## Principio

Todo el sistema se configura con **un solo archivo `.env`**. No hay URLs hardcodeadas en el código ni en el frontend.

- Frontend: rutas relativas (`/api`, `/assets`)
- Backend: lee `DATABASE_URL`, `SMTP_*`, `API_PORT`, etc. desde `.env`
- Archivos generados: carpeta `output/` relativa al proyecto

## Pasos

### 1. Copiar el proyecto

Copiar la carpeta completa excepto `venv/`.

### 2. Editar `.env`

```env
DATABASE_URL=mysql+pymysql://usuario:pass@NUEVO_HOST:3306/pago_proveedores?charset=utf8mb4
SECRET_KEY=nueva-clave-segura-de-al-menos-32-caracteres
APP_URL=http://IP-O-DOMINIO:8100
SMTP_HOST=servidor-correo.colbeef.com
SMTP_PASSWORD=contraseña-smtp
```

### 3. Base de datos

Instalación nueva: `scripts\setup.bat`

Migrar datos: `mysqldump` + `mysql` import, luego `scripts\setup.bat --skip-excel`

### 4. Arrancar

`scripts\start.bat` → http://NUEVO_SERVIDOR:8100

### 5. Auto-arranque

`scripts\install-autostart.bat` (como Administrador)
