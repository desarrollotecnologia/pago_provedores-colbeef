# Pago Proveedores — Colbeef

Aplicación web interna para administrar proveedores y lotes de pago, generar
archivos planos bancarios, notificar a los proveedores por correo y consultar
indicadores operativos.

## Contenido

- [Características](#características)
- [Tecnologías](#tecnologías)
- [Arquitectura](#arquitectura)
- [Requisitos previos](#requisitos-previos)
- [Instalación](#instalación)
- [Ejecución](#ejecución)
- [Variables de entorno](#variables-de-entorno)
- [Base de datos](#base-de-datos)
- [Flujo operativo](#flujo-operativo)
- [API y autenticación](#api-y-autenticación)
- [Scripts disponibles](#scripts-disponibles)
- [Calidad y pruebas](#calidad-y-pruebas)
- [Despliegue](#despliegue)
- [Solución de problemas](#solución-de-problemas)
- [Estado actual del repositorio](#estado-actual-del-repositorio)

## Características

- Inicio de sesión mediante JWT y control de acceso por roles.
- Administración, búsqueda y desactivación lógica de proveedores.
- Catálogos de bancos, oficinas, tipos de cuenta y tipos de identificación.
- Creación y gestión de lotes de pago.
- Registro de proveedores, conceptos e importes en cada lote.
- Generación y descarga del archivo plano requerido por el banco.
- Envío de notificaciones por correo electrónico.
- Dashboard con métricas, proveedores destacados y lotes recientes.
- Historial de pagos y auditoría de cambios de proveedores.
- Registro de telemetría y estadísticas internas de uso.

## Tecnologías

### Backend

| Tecnología | Versión | Uso |
|---|---:|---|
| Python | 3.11 o superior | Lenguaje del servidor |
| FastAPI | 0.115.6 | API REST y documentación OpenAPI |
| Uvicorn | 0.34.0 | Servidor ASGI |
| SQLAlchemy | 2.0.36 | ORM y acceso a datos |
| PyMySQL | 1.1.1 | Conector MySQL |
| Pydantic | 2.10.3 | Validación y serialización |
| PyJWT | 2.10.1 | Tokens de autenticación |
| bcrypt | 4.2.1 | Hash de contraseñas |
| xlrd | 2.0.1 | Importación de archivos Excel `.xls` |

La lista completa de dependencias se encuentra en
[`requirements.txt`](requirements.txt).

### Frontend

| Tecnología | Versión | Uso |
|---|---:|---|
| React | 18.3 | Interfaz de usuario |
| TypeScript | 5.6 | Tipado estático |
| React Router | 6.28 | Navegación del SPA |
| Chart.js | 4.4 | Gráficos del dashboard |
| Vite | 5.4 | Desarrollo y compilación |

Las dependencias y comandos del frontend están en
[`frontend/package.json`](frontend/package.json).

### Persistencia y entorno

- MySQL 8.x con tablas InnoDB y codificación `utf8mb4`.
- npm para dependencias del frontend.
- `venv` y `pip` para dependencias de Python.
- Scripts Batch para instalación y operación en Windows.
- Versión declarada de la aplicación backend: `1.3.0`.

## Arquitectura

El proyecto sigue una arquitectura cliente-servidor de tres capas:

```text
React SPA
   │ HTTP / JSON (/api)
   ▼
FastAPI ── rutas → servicios → modelos SQLAlchemy
   │
   ▼
MySQL
```

En desarrollo, Vite sirve el frontend en el puerto `5173` y redirige las
solicitudes `/api` y `/health` al backend en `8100`. En la ejecución integrada,
FastAPI sirve el contenido compilado de `frontend/dist`, la API y el fallback
de React Router desde el mismo puerto.

### Estructura del proyecto

```text
.
├── backend/
│   └── app/
│       ├── api/routes/       # Endpoints FastAPI
│       ├── core/             # Configuración, seguridad y base de datos
│       ├── models/           # Entidades SQLAlchemy
│       ├── schemas/          # Esquemas Pydantic
│       ├── seeds/            # Creación e importación de datos iniciales
│       ├── services/         # Reglas y lógica de negocio
│       ├── main.py           # Punto de entrada de la API
│       └── version.py        # Versión de la aplicación
├── database/
│   └── schema.sql            # Esquema SQL de referencia
├── docs/                     # Documentación complementaria
├── frontend/
│   ├── public/               # Recursos públicos
│   └── src/
│       ├── api/              # Cliente HTTP
│       ├── components/       # Componentes y protección de rutas
│       ├── context/          # Estado de autenticación
│       ├── pages/            # Pantallas de la aplicación
│       └── telemetry/        # Registro de eventos de uso
├── output/                   # Archivos planos generados
├── scripts/                  # Automatización para Windows
├── .env.example              # Plantilla de configuración
└── requirements.txt          # Dependencias del backend
```

## Requisitos previos

Para usar los scripts incluidos se necesita:

- Windows 10/11 o Windows Server.
- Python 3.11 o superior disponible en `PATH`.
- Node.js 18 o superior y npm.
- MySQL 8.x instalado.
- Permisos para crear la base de datos y sus tablas.
- Puerto `8100` disponible para la ejecución integrada.
- Acceso a un servidor SMTP si se enviarán correos.
- Opcional: archivo Excel `.xls` con la información inicial.

> Los scripts usan por defecto las rutas de MySQL Server 8.4. Si la instalación
> se encuentra en otra ubicación, ajuste `MYSQL_BIN` y `MYSQL_DATA` en `.env`.

## Instalación

### 1. Clonar o copiar el proyecto

```bat
git clone <URL_DEL_REPOSITORIO>
cd pago_provedores-colbeef
```

Al migrar una copia existente no incluya `venv`, `frontend/node_modules`,
archivos de logs ni secretos.

### 2. Crear la configuración local

```bat
copy .env.example .env
```

Edite `.env` y configure como mínimo:

- `DATABASE_URL`
- `SECRET_KEY`
- `APP_URL`
- Las variables `SMTP_*` si se enviarán correos

Genere una clave secreta aleatoria y no la comparta ni la almacene en Git.

### 3. Ejecutar la instalación automatizada

Instalación sin importar Excel:

```bat
scripts\setup.bat --skip-excel
```

Instalación con un archivo Excel:

```bat
scripts\setup.bat --excel "C:\datos\proveedores.xls"
```

El script:

1. Crea el entorno virtual `venv`.
2. Instala las dependencias de Python.
3. Intenta iniciar MySQL.
4. Crea la base de datos, tablas, catálogos y usuarios iniciales.
5. Importa el Excel cuando se proporciona.
6. Instala las dependencias y compila el frontend.

> Use `--skip-excel` cuando no tenga un archivo válido. La ejecución sin este
> argumento intentará importar la ruta configurada en `EXCEL_PATH`.

### Formato del Excel inicial

El importador espera un archivo `.xls` con estas hojas:

- `Bancos`
- `Oficinas`
- `Cuentas Ordenantes`
- `Beneficiarios`

Antes de importar, puede revisar el archivo con:

```bat
scripts\validate_excel.bat
```

## Ejecución

### Aplicación integrada

```bat
scripts\start.bat
```

Direcciones predeterminadas:

- Aplicación: <http://localhost:8100>
- Swagger UI: <http://localhost:8100/docs>
- ReDoc: <http://localhost:8100/redoc>
- Estado del servicio: <http://localhost:8100/health>

Para detener o reiniciar:

```bat
scripts\stop.bat
scripts\restart.bat
```

### Desarrollo del backend

```bat
venv\Scripts\activate
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8100 --reload
```

### Desarrollo del frontend

En otra terminal:

```bat
cd frontend
npm install
npm run dev
```

Abra <http://localhost:5173>. El proxy de Vite enviará las solicitudes al
backend en <http://localhost:8100>.

### Compilar el frontend

```bat
cd frontend
npm run build
```

También puede usar:

```bat
scripts\build_frontend.bat
```

## Variables de entorno

La plantilla completa está en [`.env.example`](.env.example).

### Aplicación y seguridad

| Variable | Requerida | Descripción |
|---|---:|---|
| `DATABASE_URL` | Sí | URL SQLAlchemy de conexión a MySQL |
| `SECRET_KEY` | Sí | Clave usada para firmar los JWT; mínimo 32 caracteres |
| `APP_URL` | Sí | URL pública de la aplicación |
| `APP_NAME` | No | Nombre mostrado por la aplicación |
| `APP_ENV` | No | Entorno, por ejemplo `development` o `production` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | Duración del token; plantilla: 480 minutos |

Ejemplo seguro:

```env
DATABASE_URL=mysql+pymysql://app_user:example_password@localhost:3306/pago_proveedores?charset=utf8mb4
SECRET_KEY=reemplazar-por-una-clave-aleatoria-de-al-menos-32-caracteres
APP_URL=http://localhost:8100
APP_NAME=Pago Proveedores
APP_ENV=development
ACCESS_TOKEN_EXPIRE_MINUTES=480
```

### Red, archivos y CORS

| Variable | Descripción |
|---|---|
| `API_HOST` | Interfaz de red deseada |
| `API_PORT` | Puerto HTTP; valor habitual: `8100` |
| `CORS_ORIGINS` | Orígenes permitidos separados según la configuración backend |
| `OUTPUT_DIR` | Directorio de archivos planos generados |
| `STATIC_DIR` | Directorio del frontend compilado |
| `CIUDAD_DEFAULT` | Ciudad usada al generar información bancaria |

> Actualmente `scripts/start.bat` usa siempre `0.0.0.0` como host aunque
> `API_HOST` tenga otro valor.

### Correo SMTP

| Variable | Descripción |
|---|---|
| `SMTP_HOST` | Host del servidor SMTP |
| `SMTP_PORT` | Puerto SMTP, normalmente `587` |
| `SMTP_USER` | Usuario SMTP |
| `SMTP_PASSWORD` | Contraseña SMTP |
| `SMTP_FROM_EMAIL` | Dirección remitente |
| `SMTP_FROM_NAME` | Nombre del remitente |
| `SMTP_USE_TLS` | Activa STARTTLS |

Las variables `EMAIL_FIRMA_*` personalizan el nombre, cargo, empresa, teléfono,
dirección, sitio web y banner de la firma HTML.

Nunca confirme en Git el archivo `.env`, contraseñas SMTP, claves JWT ni
credenciales de base de datos.

## Base de datos

El sistema trabaja con MySQL y modela las siguientes entidades principales:

- Usuarios y roles.
- Bancos, oficinas, tipos de identificación y tipos de cuenta.
- Cuentas ordenantes.
- Proveedores.
- Lotes y pagos.
- Envíos de correo.
- Configuración.
- Eventos de usabilidad.
- Cambios auditados de proveedores.

También existe una vista de resumen de lotes: `vw_resumen_lotes`.

### Inicialización manual

Desde la raíz del proyecto:

```bat
venv\Scripts\activate
cd backend
python -m app.seeds.run_seed --skip-excel
```

Opciones disponibles:

```text
--excel RUTA        Importa un archivo Excel específico
--skip-excel        Omite la importación
--skip-create-db    No intenta crear la base de datos
```

La inicialización crea tablas mediante SQLAlchemy y aplica ajustes imperativos
desde los seeders. Aunque `alembic` aparece en las dependencias, actualmente no
existen `alembic.ini` ni revisiones versionadas; por tanto, no hay un flujo de
migraciones Alembic operativo.

## Flujo operativo

1. Un administrador inicia sesión.
2. Crea un lote indicando fecha, cuenta ordenante y concepto.
3. Agrega proveedores e importes.
4. Revisa y confirma el lote.
5. Genera y descarga el archivo plano bancario.
6. Envía los correos a los proveedores o procesa ambas acciones.
7. Consulta estados, historial y errores desde la aplicación.

Estados contemplados para un lote:

```text
borrador → confirmado → archivo_generado → correos_enviados → completado
                                                            ↘ anulado
```

La interfaz presenta el proceso como “Pagos del viernes”, pero el backend no
impone actualmente una validación que limite la fecha al viernes.

El TXT bancario se genera con saltos de línea CRLF, codificación Latin-1 y
registros base de 281 caracteres. No cambie su formato sin validarlo con la
entidad bancaria.

## API y autenticación

Todos los endpoints funcionales usan el prefijo `/api`. La especificación
actualizada puede consultarse en `/docs` o `/redoc` mientras el servidor está
en ejecución.

### Endpoints principales

- `POST /api/auth/login`: inicio de sesión.
- `GET /api/auth/me`: usuario autenticado.
- `/api/proveedores`: gestión de proveedores.
- `/api/catalogos/*`: bancos y catálogos asociados.
- `/api/lotes`: gestión de lotes.
- `/api/lotes/{id}/pagos`: pagos de un lote.
- `/api/lotes/{id}/generar-archivo`: generación del TXT.
- `/api/lotes/{id}/descargar-archivo`: descarga del TXT.
- `/api/lotes/{id}/enviar-correos`: notificación por correo.
- `/api/lotes/{id}/procesar`: generación y envío.
- `/api/historial/pagos`: historial.
- `/api/cambios/proveedores`: auditoría.
- `/api/usability/event`: registro de telemetría.
- `GET /health`: versión y estado básico del servicio.

### Seguridad

- Autenticación Bearer mediante JWT firmado con HS256.
- Contraseñas almacenadas con bcrypt.
- Roles definidos: `admin` y `operador`.
- Protección de rutas tanto en FastAPI como en React.
- La sesión del frontend se mantiene en memoria; al recargar la página es
  necesario volver a iniciar sesión.

Los seeders crean usuarios iniciales. Sus contraseñas deben cambiarse
inmediatamente después de instalar la aplicación y no deben publicarse en la
documentación.

## Scripts disponibles

| Script | Función |
|---|---|
| `setup.bat` | Crea el entorno, instala dependencias, prepara la BD y compila |
| `start.bat` | Inicia MySQL, FastAPI y abre la aplicación |
| `stop.bat` | Detiene el proceso que escucha en el puerto de la aplicación |
| `restart.bat` | Detiene y vuelve a iniciar la aplicación |
| `build_frontend.bat` | Instala dependencias y compila el frontend |
| `update.bat` | Actualiza dependencias Python y reinicia |
| `update_server.bat` | Actualiza código, esquema, frontend y servicio |
| `start_mysql.bat` | Inicia MySQL usando las rutas configuradas |
| `verify_db.bat` | Consulta el estado y los conteos de la base de datos |
| `validate_excel.bat` | Valida o compara el Excel operativo |
| `verify_deploy.bat` | Comprueba artefactos de despliegue |
| `install_email_banner.bat` | Instala recursos gráficos del correo |
| `uninstall-autostart.bat` | Elimina la tarea programada de autoarranque |

Los archivos `install-autostart.bat` y `start-autostart.bat` aparecen en
documentación anterior, pero no están presentes en este repositorio.

## Calidad y pruebas

Comandos de compilación disponibles:

```bat
cd frontend
npm run build
```

Estado actual:

- No hay una suite automatizada de pruebas para backend o frontend.
- No existen scripts configurados de lint o formateo.
- No hay configuración de integración continua.
- El build de Vite no ejecuta un `tsc --noEmit` explícito.

Antes de desplegar cambios se recomienda, como mínimo:

1. Compilar el frontend.
2. Iniciar el backend y verificar `/health`.
3. Revisar el flujo de login.
4. Crear un lote de prueba.
5. Generar y validar un archivo plano en un entorno no productivo.
6. Probar SMTP con destinatarios controlados.

## Despliegue

El repositorio está orientado a un despliegue manual en Windows:

1. Copiar o actualizar el proyecto.
2. Crear y completar `.env`.
3. Restaurar la base de datos si corresponde.
4. Ejecutar `scripts\setup.bat --skip-excel`.
5. Ejecutar `scripts\start.bat`.
6. Verificar `/health`, `/docs` y el acceso a la interfaz.

Consulte [docs/MIGRACION.md](docs/MIGRACION.md) para el procedimiento de
migración de servidor.

No se incluyen actualmente Dockerfile, Docker Compose, proxy Nginx/IIS,
servicio de Windows completo ni pipeline CI/CD. El comando de `start.bat`
activa `--reload`; para producción se recomienda ejecutar Uvicorn sin recarga
automática y administrar el proceso con un servicio supervisado.

## Solución de problemas

### El backend no inicia

- Verifique que existan los módulos indicados en
  [Estado actual del repositorio](#estado-actual-del-repositorio).
- Confirme que el entorno virtual esté activo.
- Revise `DATABASE_URL` y que MySQL esté escuchando.
- Compruebe que el puerto configurado no esté ocupado.

### No se puede conectar a MySQL

- Ajuste `MYSQL_BIN` y `MYSQL_DATA` si MySQL no está instalado en las rutas
  predeterminadas.
- Compruebe usuario, contraseña, host, puerto y nombre de base en
  `DATABASE_URL`.
- Ejecute `scripts\verify_db.bat`.

### El frontend no aparece

Compile los recursos y reinicie:

```bat
scripts\build_frontend.bat
scripts\restart.bat
```

FastAPI espera encontrar `frontend/dist/index.html`.

### La importación Excel falla

- Confirme que el archivo sea `.xls`; `xlrd` no admite todos los formatos
  modernos de Excel.
- Revise los nombres exactos de las hojas requeridas.
- Use `--skip-excel` si la importación no aplica.

### No se envían correos

- Complete todas las variables `SMTP_*`.
- Compruebe host, puerto, TLS y credenciales.
- Verifique que el servidor permita la dirección configurada como remitente.
- Pruebe primero con destinatarios controlados.

### El archivo bancario contiene caracteres incorrectos

El formato usa Latin-1 por compatibilidad bancaria. Verifique que nombres,
conceptos y ciudades puedan representarse en esa codificación.

## Estado actual del repositorio

> **Importante:** la copia revisada está incompleta. Faltan estos módulos
> importados por el backend:
>
> - `backend/app/core/config.py`
> - `backend/app/services/config_service.py`
>
> Mientras no se recuperen o implementen, el backend no podrá iniciar y no es
> posible garantizar que la instalación documentada termine correctamente.

También se identificaron estas limitaciones:

- No hay migraciones Alembic configuradas.
- Faltan los scripts de instalación y arranque automático mencionados en
  documentación anterior.
- `scripts/verify_deploy.bat` valida versiones antiguas y puede reportar un
  fallo aunque el build actual sea correcto.
- `scripts/update.bat` no compila el frontend ni aplica cambios de esquema;
  para una actualización integral se usa `scripts/update_server.bat`.

## Documentación adicional

- [Migración entre servidores](docs/MIGRACION.md)
- [Documentación de usabilidad y telemetría](docs/USABILIDAD.md)

## Licencia

No se encontró un archivo de licencia en el repositorio. El uso, distribución
y modificación deben ajustarse a las políticas internas de Colbeef y a los
términos definidos por los responsables del proyecto.
