"""Registro y consulta de cambios en proveedores (auditoría)."""
from __future__ import annotations

import math
from datetime import date, datetime
from typing import Any

from fastapi import HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import Banco, CambioProveedor, Proveedor, TipoCuenta, TipoIdentificacion, Usuario
from app.schemas.cambios import (
    CambioCampo,
    CambioProveedorDetalle,
    CambioProveedorItem,
    CambiosProveedorResponse,
    CambiosResumen,
)

CAMPOS_AUDIT = (
    "identificacion",
    "tipo_identificacion",
    "digito_verificacion",
    "razon_social",
    "forma_pago",
    "banco_codigo",
    "tipo_cuenta",
    "numero_cuenta",
    "cod_oficina",
    "email",
    "activo",
)

CAMPOS_ETIQUETAS: dict[str, str] = {
    "identificacion": "Identificación",
    "tipo_identificacion": "Tipo ID",
    "digito_verificacion": "Dígito verificación",
    "razon_social": "Razón social",
    "forma_pago": "Forma de pago",
    "banco_codigo": "Banco",
    "tipo_cuenta": "Tipo de cuenta",
    "numero_cuenta": "Número de cuenta",
    "cod_oficina": "Código oficina",
    "email": "Correo",
    "activo": "Activo",
}


def _normalizar_rango(fecha_desde: date, fecha_hasta: date) -> tuple[date, date]:
    if fecha_hasta < fecha_desde:
        raise HTTPException(
            status_code=400,
            detail="La fecha hasta no puede ser anterior a la fecha desde",
        )
    return fecha_desde, fecha_hasta


def _valor_raw(proveedor: Proveedor, campo: str) -> Any:
    return getattr(proveedor, campo)


def proveedor_snapshot(proveedor: Proveedor) -> dict[str, Any]:
    return {campo: _valor_raw(proveedor, campo) for campo in CAMPOS_AUDIT}


def _format_valor(db: Session, campo: str, valor: Any) -> str | None:
    if valor is None:
        return None
    if campo == "tipo_identificacion":
        tipo = db.get(TipoIdentificacion, int(valor))
        return tipo.descripcion if tipo else str(valor)
    if campo == "tipo_cuenta":
        tipo = db.get(TipoCuenta, int(valor))
        return tipo.descripcion if tipo else str(valor)
    if campo == "banco_codigo":
        banco = db.get(Banco, int(valor))
        return f"{valor} — {banco.descripcion}" if banco else str(valor)
    if campo == "activo":
        return "Sí" if valor else "No"
    if campo == "cod_oficina" and valor == "":
        return None
    return str(valor)


def _diff_cambios(
    db: Session, antes: dict[str, Any], despues: dict[str, Any]
) -> list[dict[str, Any]]:
    cambios: list[dict[str, Any]] = []
    for campo in CAMPOS_AUDIT:
        a, d = antes.get(campo), despues.get(campo)
        if a != d:
            cambios.append(
                {
                    "campo": campo,
                    "etiqueta": CAMPOS_ETIQUETAS[campo],
                    "anterior": _format_valor(db, campo, a),
                    "nuevo": _format_valor(db, campo, d),
                }
            )
    return cambios


def _cambios_creacion(db: Session, snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "campo": campo,
            "etiqueta": CAMPOS_ETIQUETAS[campo],
            "anterior": None,
            "nuevo": _format_valor(db, campo, snapshot.get(campo)),
        }
        for campo in CAMPOS_AUDIT
        if snapshot.get(campo) is not None and snapshot.get(campo) != ""
    ]


def _resumen(accion: str, cambios: list[dict[str, Any]] | None) -> str:
    if accion == "crear":
        return "Proveedor creado"
    if accion == "desactivar":
        return "Proveedor desactivado"
    n = len(cambios or [])
    if n == 0:
        return "Edición sin cambios detectados"
    if n == 1:
        return f"1 campo modificado: {cambios[0]['etiqueta']}"
    return f"{n} campos modificados"


def registrar_creacion(db: Session, proveedor: Proveedor, usuario_id: int) -> None:
    snap = proveedor_snapshot(proveedor)
    cambios = _cambios_creacion(db, snap)
    db.add(
        CambioProveedor(
            proveedor_id=proveedor.id,
            usuario_id=usuario_id,
            accion="crear",
            razon_social=proveedor.razon_social,
            identificacion=proveedor.identificacion,
            cambios=cambios,
            snapshot=snap,
        )
    )


def registrar_edicion(
    db: Session,
    proveedor: Proveedor,
    antes: dict[str, Any],
    usuario_id: int,
) -> None:
    despues = proveedor_snapshot(proveedor)
    cambios = _diff_cambios(db, antes, despues)
    if not cambios:
        return
    db.add(
        CambioProveedor(
            proveedor_id=proveedor.id,
            usuario_id=usuario_id,
            accion="editar",
            razon_social=proveedor.razon_social,
            identificacion=proveedor.identificacion,
            cambios=cambios,
            snapshot=despues,
        )
    )


def registrar_desactivacion(db: Session, proveedor: Proveedor, usuario_id: int) -> None:
    db.add(
        CambioProveedor(
            proveedor_id=proveedor.id,
            usuario_id=usuario_id,
            accion="desactivar",
            razon_social=proveedor.razon_social,
            identificacion=proveedor.identificacion,
            cambios=[
                {
                    "campo": "activo",
                    "etiqueta": CAMPOS_ETIQUETAS["activo"],
                    "anterior": "Sí",
                    "nuevo": "No",
                }
            ],
            snapshot=proveedor_snapshot(proveedor),
        )
    )


def _to_item(row: CambioProveedor, usuario: Usuario) -> CambioProveedorItem:
    cambios = row.cambios or []
    return CambioProveedorItem(
        id=row.id,
        registrado_en=row.registrado_en,
        accion=row.accion,
        proveedor_id=row.proveedor_id,
        razon_social=row.razon_social,
        identificacion=row.identificacion,
        usuario_id=row.usuario_id,
        usuario_nombre=usuario.nombre_completo,
        resumen=_resumen(row.accion, cambios),
        cantidad_cambios=len(cambios),
    )


def buscar_cambios(
    db: Session,
    *,
    fecha_desde: date,
    fecha_hasta: date,
    page: int = 1,
    page_size: int = 50,
    q: str | None = None,
) -> CambiosProveedorResponse:
    fecha_desde, fecha_hasta = _normalizar_rango(fecha_desde, fecha_hasta)
    inicio = datetime.combine(fecha_desde, datetime.min.time())
    fin = datetime.combine(fecha_hasta, datetime.max.time())

    filtros = [
        CambioProveedor.registrado_en >= inicio,
        CambioProveedor.registrado_en <= fin,
    ]
    if q:
        term = f"%{q.strip()}%"
        filtros.append(
            or_(
                CambioProveedor.razon_social.ilike(term),
                CambioProveedor.identificacion.ilike(term),
            )
        )

    total = db.scalar(select(func.count(CambioProveedor.id)).where(*filtros)) or 0
    page_size = min(max(page_size, 1), 100)
    page = max(page, 1)
    pages = math.ceil(total / page_size) if total else 0
    offset = (page - 1) * page_size

    rows = db.execute(
        select(CambioProveedor, Usuario)
        .join(Usuario, CambioProveedor.usuario_id == Usuario.id)
        .where(*filtros)
        .order_by(CambioProveedor.registrado_en.desc(), CambioProveedor.id.desc())
        .offset(offset)
        .limit(page_size)
    ).all()

    items = [_to_item(c, u) for c, u in rows]

    resumen_acciones = db.execute(
        select(CambioProveedor.accion, func.count(CambioProveedor.id))
        .where(*filtros)
        .group_by(CambioProveedor.accion)
    ).all()
    por_accion = {accion: count for accion, count in resumen_acciones}

    return CambiosProveedorResponse(
        resumen=CambiosResumen(
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            cantidad_cambios=total,
            creaciones=por_accion.get("crear", 0),
            ediciones=por_accion.get("editar", 0),
            desactivaciones=por_accion.get("desactivar", 0),
        ),
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


def obtener_detalle(db: Session, cambio_id: int) -> CambioProveedorDetalle | None:
    row = db.execute(
        select(CambioProveedor, Usuario)
        .join(Usuario, CambioProveedor.usuario_id == Usuario.id)
        .where(CambioProveedor.id == cambio_id)
    ).first()
    if not row:
        return None
    cambio, usuario = row
    base = _to_item(cambio, usuario)
    campos = [CambioCampo.model_validate(c) for c in (cambio.cambios or [])]
    return CambioProveedorDetalle(
        **base.model_dump(),
        cambios=campos,
        snapshot=cambio.snapshot,
    )
