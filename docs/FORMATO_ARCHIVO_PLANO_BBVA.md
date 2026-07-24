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
| 6 | Cuenta BBVA | 16 | Ceros si el banco no es BBVA (`0013`) |
| 7 | Tipo cuenta ACH | 2 | Columna G, formato `00` (`01`/`02`) |
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

## Codificación y fin de línea

- Codificación: Latin-1
- Separador de líneas: CRLF (`\r\n`), como `Print #` de VBA

## Verificación

```bat
cd backend
set PYTHONPATH=.
python scripts_verify_archivo_plano.py
```
