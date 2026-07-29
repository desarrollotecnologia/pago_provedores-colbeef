"""Normalización de una o varias facturas en un pago."""
from __future__ import annotations

FACTURA_SEPARATOR = ", "
MAX_FACTURAS = 20
MAX_FACTURA_LEN = 80
MAX_FACTURAS_JOINED_LEN = 500


def split_facturas(valor: str | None) -> list[str]:
    if not valor:
        return []
    partes: list[str] = []
    for bruto in str(valor).replace(";", ",").replace("|", ",").split(","):
        texto = bruto.strip()
        if texto and texto not in partes:
            partes.append(texto)
    return partes


def join_facturas(facturas: list[str]) -> str:
    limpios = [f.strip() for f in facturas if f and str(f).strip()]
    # únicos preservando orden
    vistos: set[str] = set()
    ordenados: list[str] = []
    for f in limpios:
        key = f.casefold()
        if key in vistos:
            continue
        vistos.add(key)
        ordenados.append(f[:MAX_FACTURA_LEN])
    joined = FACTURA_SEPARATOR.join(ordenados[:MAX_FACTURAS])
    return joined[:MAX_FACTURAS_JOINED_LEN]


def normalize_facturas_input(
    *,
    facturas: list[str] | None = None,
    numero_factura: str | None = None,
) -> list[str]:
    if facturas is not None:
        items = join_facturas(facturas)
        return split_facturas(items)
    return split_facturas(numero_factura)


def etiqueta_facturas(facturas: list[str] | str | None) -> str:
    items = split_facturas(facturas) if isinstance(facturas, str) or facturas is None else [
        f.strip() for f in facturas if f and str(f).strip()
    ]
    if not items:
        return ""
    return join_facturas(items)
