# Telemetría de usabilidad

Sistema ligero para medir adopción y uso de **Pago Proveedores - Colbeef**.

## Qué registra

| Acción | Cuándo |
|--------|--------|
| `session_start` | Al iniciar sesión |
| `module_open` | Al cambiar de pantalla (automático) |
| `action_complete` | Acciones críticas (crear lote, generar archivo, etc.) |
| `error_ui` | Errores visibles (opcional) |
| `admin_open` | Al abrir el dashboard de usabilidad |

**No se registran:** contraseñas, tokens ni datos personales sensibles.

## Endpoints API

| Método | Ruta | Acceso |
|--------|------|--------|
| POST | `/api/usability/event` | Usuario autenticado (cualquier rol) |
| GET | `/api/usability/stats?days=30` | Solo **admin** |

## Retención

- Máximo **50.000** eventos
- Máximo **90 días** de antigüedad
- Limpieza automática al insertar

## Dashboard de usabilidad

- Ruta: `/usabilidad` (solo administrador)
- Atajo oculto: **Ctrl + Shift + U** (solo admin)
- Filtros: 7 / 30 / 90 días

## Tabla en MySQL

Al actualizar, crear la tabla nueva:

```bat
cd backend
..\venv\Scripts\activate
python -c "from app.seeds.setup_database import create_tables; create_tables()"
```

## Añadir tracking a un módulo nuevo

```typescript
import { track, trackAction } from "../telemetry/tracker";

// Navegación automática (ya activo en Layout vía usePageTracking)

// Acción manual
trackAction("mi_modulo", "Descripción de la acción", { id: 123 });

// Error visible
import { trackError } from "../telemetry/tracker";
trackError("mi_modulo", "Mensaje de error mostrado al usuario");
```

## Usuario `panel` (operador)

Solo ve la **guía de usabilidad**. Sus eventos (`session_start`, `module_open` en `guia_uso`) permiten medir si consultan la guía.

## Usuario `viviana` (admin)

Opera el sistema y accede al dashboard de telemetría en **Usabilidad** (menú discreto al final).
