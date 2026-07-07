# Pago Proveedores - Colbeef

Sistema completo de pagos a proveedores: lotes, archivo plano bancario, correos y dashboard.

## Migración fácil

**Solo editar `.env` en el servidor nuevo.** El frontend usa `/api` (ruta relativa) y el backend lee todo desde variables de entorno.

Ver [docs/MIGRACION.md](docs/MIGRACION.md)

## Inicio rápido

```bat
copy .env.example .env
:: Editar DATABASE_URL, SECRET_KEY y SMTP
scripts\setup.bat
scripts\start.bat
```

Abrir: **http://localhost:8100** (app + API en el mismo puerto)

Swagger API: **http://localhost:8100/docs**

## Usuarios de prueba

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| `viviana` / `VIVIANA ANDREA` | `Colbeef2026*` | admin |
| `panel` | `123456789` | operador |

## Módulos

| Módulo | Descripción |
|--------|-------------|
| Dashboard | Métricas, top proveedores, últimos lotes |
| Proveedores | CRUD + búsqueda |
| Pagos | Lotes del viernes, archivo plano, correos |
| Config | Todo vía `.env` |

## Scripts

| Script | Función |
|--------|---------|
| `setup.bat` | Instala deps + BD + Excel |
| `start.bat` | MySQL + API + abre navegador |
| `stop.bat` | Detiene el servicio |
| `restart.bat` | Reinicia |
| `update.bat` | Actualiza deps y reinicia |
| `start-autostart.bat` | Arranque silencioso (sin navegador, para servidor) |
| `install-autostart.bat` | Registra auto-arranque al reiniciar Windows (Admin) |
| `uninstall-autostart.bat` | Quita el auto-arranque (Admin) |
| `verify_db.bat` | Estado de la BD |

## Variables .env principales

| Variable | Descripción |
|----------|-------------|
| `DATABASE_URL` | MySQL del servidor |
| `SECRET_KEY` | JWT (mín. 32 chars) |
| `APP_URL` | URL pública (`http://servidor:8100`) |
| `API_PORT` | Puerto (default 8100) |
| `SMTP_*` | Correos a proveedores |
| `OUTPUT_DIR` | Archivos planos (relativo) |
| `STATIC_DIR` | Frontend (relativo) |

## Flujo operativo (viernes)

1. **Pagos** → Nuevo lote
2. Agregar proveedores e importes
3. **Generar archivo plano** → descargar TXT para el banco
4. **Enviar correos** o **Procesar todo** (archivo + correos)

## API

Prefijo: `/api` — ver `/docs` para detalle completo.
