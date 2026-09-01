# Formato archivo plano BBVA (Planocash)

Extraído de las macros VBA del Excel
`MODELO PAGO PROVEEDORES.xls`, rutina **`Planocash`** (`Módulo2`).

El programa replica esta estructura en
`backend/app/services/archivo_plano_service.py`.

## Orden de campos (una línea por pago)

| # | Campo | Longitud | Origen Excel / regla |
|---|---|---:|---|
| 1 | Tipo identificación | 2 | Columna B, formato `00` |
| 2 | Identificación | 15 | Columna A, formato `000000000000000` (sin DV) |
| 3 | Dígito verificación | 1 | Columna C |
| 4 | Forma de pago | 1 | Columna E (`1` abono cuenta; **no** se rellena a 2) |
| 5 | Banco | 4 | Columna F, formato `0000` (si forma ≠ 1 → `0013`) |
| 6 | Cuenta BBVA | 16 | Solo si banco = `0013`. Ver estructura abajo. Ceros si es otro banco |
| 7 | Tipo cuenta ACH | 2 | Columna G, formato `00` (`01` corriente, `02` ahorros) |
| 8 | Número cuenta ACH | 17 | Columna H, relleno con **espacios a la derecha** |
| 9 | Importe | 15 | Entero + 2 decimales, sin punto, ceros a la izquierda |
| 10 | Año / Mes / Día | 4+2+2 | Para forma `1`: `0000` `00` `00` |
| 11 | Código oficina | 4 | Para forma `1`: `0000`; forma `3`: `9999` |
| 12 | Nombre beneficiario | 36 | Columna D, espacios a la derecha |
| 13 | Dirección 1 | 36 | Fijo `BOGOTA` + espacios (ciudad del sistema) |
| 14 | Dirección 2 | 36 | Espacios |
| 15 | E-mail | 48 | Columna R, espacios a la derecha |
| 16 | Concepto 1..4 | 40 c/u | Solo si tienen texto; espacios a la derecha |

Con un solo concepto la línea mide **281** caracteres.

### Bloque Cuenta BBVA (16 caracteres, macro `Hallardatoscuenta`)

Solo cuando el banco es `0013` (BBVA) y forma de pago = `1`:

```
Oficina (4) + "00" + Tipo cuenta (4) + Últimos 6 dígitos cuenta (6)
```

| Parte | Origen | Ejemplo |
|---|---|---|
| Oficina | `"0"` + primeros 3 dígitos de la cuenta | cuenta `232217414` → `0232` |
| Separador | fijo `00` | `00` |
| Tipo cuenta | columna G con formato `00` + `00` | corriente `01` → `0100`; ahorros `02` → `0200` |
| Número | últimos 6 dígitos de la cuenta | `217414` |

Ejemplo completo: cuenta `232217414`, tipo `02` → `0232000200217414`

**Importante:** el tipo va como `01`/`02` (dos dígitos), no como `1`/`2`. Si se usa un solo dígito queda un cero de más al rellenar el campo.

## Codificación y fin de línea

- Codificación: Latin-1
- Separador de líneas: CRLF (`\r\n`), como `Print #` de VBA

## Verificación

```bat
cd backend
set PYTHONPATH=.
python scripts_verify_archivo_plano.py
```
