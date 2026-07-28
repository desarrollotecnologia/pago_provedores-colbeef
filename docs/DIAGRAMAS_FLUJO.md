# Diagramas de flujo — Pago Proveedores Colbeef

Documentación visual del sistema. Los diagramas usan [Mermaid](https://mermaid.js.org/) y se ven en GitHub, Cursor, VS Code y [mermaid.live](https://mermaid.live).

---

## 1. Visión general del sistema

```mermaid
flowchart TB
    U[Usuario] --> FE[Frontend React<br/>Vite SPA]
    FE -->|HTTP /api| BE[Backend FastAPI]
    BE --> DB[(MySQL)]
    BE --> OUT[Archivo plano TXT<br/>carpeta output]
    BE --> SMTP[Correo SMTP<br/>notificación a proveedores]
    OUT --> BBVA[Plataforma BBVA<br/>pagos masivos]
```

---

## 2. Acceso y roles

```mermaid
flowchart TD
    A([Abrir aplicación]) --> B[Pantalla Login]
    B --> C{Credenciales<br/>válidas?}
    C -->|No| B
    C -->|Sí| D{Rol del usuario}
    D -->|admin| E[Dashboard ejecutivo]
    D -->|operador / supervisor| F[Dashboard usabilidad]
    E --> G[Menú: Proveedores · Pagos · Historial · Cambios]
    F --> H[Solo consulta de telemetría]
```

| Rol | Pantalla de inicio | Puede operar pagos |
|---|---|---|
| Administrador | Dashboard del día | Sí |
| Supervisor (operador) | Usabilidad | No |

---

## 3. Navegación por vistas (Administrador)

```mermaid
flowchart LR
    LOGIN[/login/] --> HOME[/ Dashboard /]
    HOME --> PROV[/proveedores/]
    HOME --> PAGOS[/pagos/]
    PAGOS --> DETALLE[/pagos/:id/]
    HOME --> HIST[/historial/]
    HOME --> CAMB[/cambios/]
```

---

## 4. Flujo principal: pago semanal

Este es el proceso operativo más importante del sistema.

```mermaid
flowchart TD
    A([Inicio de sesión admin]) --> B[Ir a Pagos]
    B --> C[Crear nuevo lote]
    C --> D[Fecha · Cuenta ordenante · Concepto]
    D --> E[Abrir detalle del lote]
    E --> F[Agregar pago]
    F --> G[Buscar proveedor]
    G --> H[Importe · Factura · Concepto · Email]
    H --> I{¿Más proveedores?}
    I -->|Sí| F
    I -->|No| J{¿Pagos incompletos?}
    J -->|Sí| K[Editar filas incompletas]
    K --> J
    J -->|No| L[Finalizar lote]
    L --> M[Generar archivo plano TXT]
    M --> N[Descargar TXT]
    N --> O[Enviar correos a proveedores]
    O --> P[Cargar TXT en BBVA]
    P --> Q([Fin del ciclo])
```

### Alternativa avanzada (mismo detalle de lote)

```mermaid
flowchart TD
    A[Lote con pagos completos] --> B{Acción}
    B -->|Finalizar lote| C[Archivo + descarga + correos]
    B -->|Solo generar archivo| D[Crear TXT]
    D --> E[Descargar TXT]
    E --> F[Solo enviar correos]
    C --> G([Lote cerrado])
    F --> G
```

---

## 5. Estados del lote

```mermaid
stateDiagram-v2
    [*] --> borrador: Crear lote
    borrador --> confirmado: Confirmar / generar archivo
    borrador --> archivo_generado: Generar archivo
    confirmado --> archivo_generado: Generar archivo
    archivo_generado --> correos_enviados: Enviar correos
    archivo_generado --> completado: Procesar todo
    correos_enviados --> completado: Cierre
    borrador --> anulado: Anular
    confirmado --> anulado: Anular

    note right of borrador
      Se pueden agregar,
      editar o quitar pagos
    end note
```

---

## 6. Flujo de proveedores

```mermaid
flowchart TD
    A[Vista Proveedores] --> B{Acción}
    B -->|Buscar| C[Filtrar por nombre / NIT / cuenta]
    B -->|Nuevo| D[Formulario alta]
    B -->|Editar| E[Formulario edición]
    D --> F[Tipo ID · Identificación]
    F --> G{¿Es NIT 03 o 09?}
    G -->|Sí| H[Calcular DV DIAN automático]
    G -->|No| I[DV = 0]
    H --> J[Banco · Cuenta · Email]
    I --> J
    J --> K[Guardar]
    K --> L[Auditoría en Cambios]
    K --> M[Lista se filtra al proveedor guardado]
    E --> K
```

---

## 7. Generación del archivo plano (BBVA Planocash)

```mermaid
flowchart TD
    A[Pagos del lote activos] --> B[Por cada pago]
    B --> C[Armar línea fijo-ancho]
    C --> D[Tipo ID + Identificación + DV + Forma + Banco]
    D --> E[Cuenta BBVA / ACH + Tipo cuenta + Nº cuenta]
    E --> F[Importe en centavos 15 dígitos]
    F --> G[Fecha · Oficina · Nombre · Ciudad · Email · Concepto]
    G --> H[Escribir TXT Latin-1 CRLF]
    H --> I[Descarga / carpeta output]
    I --> J[Carga en plataforma BBVA]
```

Detalle de campos: [FORMATO_ARCHIVO_PLANO_BBVA.md](FORMATO_ARCHIVO_PLANO_BBVA.md)

---

## 8. Arquitectura de capas (backend)

```mermaid
flowchart TB
    R[Rutas API<br/>api/routes] --> S[Servicios<br/>services]
    S --> M[Modelos SQLAlchemy<br/>models]
    S --> SCH[Schemas Pydantic<br/>schemas]
    M --> DB[(MySQL)]
    S --> AP[archivo_plano_service]
    S --> EM[email_service]
    S --> AU[auth_service]
```

---

## 9. Consultas posteriores al pago

```mermaid
flowchart TD
    A[Después del ciclo] --> B{Necesidad}
    B -->|Ver pagos de otros días| C[Historial]
    C --> D[Rango de fechas + filtro]
    D --> E[Detalle de pago / lote / archivo]
    B -->|Quién cambió un proveedor| F[Cambios]
    F --> G[Creaciones · Ediciones · Desactivaciones]
    B -->|Resumen del día| H[Dashboard]
```

---

## Cómo ver estos diagramas

1. **En Cursor / VS Code:** abrir este archivo; la vista previa de Markdown renderiza Mermaid.
2. **En GitHub:** al subir el `.md`, los diagramas se muestran solos.
3. **Exportar imagen/PDF:** copiar un bloque Mermaid en [https://mermaid.live](https://mermaid.live) → Export PNG/SVG.

---

## Relación con el manual de usuario

| Diagrama | Manual |
|---|---|
| Acceso y roles | Secciones 2 y 11 |
| Pago semanal | Secciones 6, 7 y 8 |
| Proveedores | Sección 5 |
| Archivo plano | Sección 7.4 y doc BBVA |
