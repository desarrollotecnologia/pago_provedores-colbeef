"""Servicio de lotes y pagos semanales."""
from __future__ import annotations

import math
from datetime import date
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.models import CuentaOrdenante, LotePago, Pago, Proveedor
from app.schemas.lotes import LoteCreate, LoteUpdate, PagoItemCreate, PagoItemUpdate
from app.services.archivo_plano_service import _campo_identificacion, build_payment_line
from app.services.config_service import get_campo_factura


def _snapshot_proveedor(proveedor: Proveedor) -> dict:
    return {
        "identificacion": proveedor.identificacion,
        "tipo_identificacion": proveedor.tipo_identificacion,
        "digito_verificacion": proveedor.digito_verificacion,
        "razon_social": proveedor.razon_social,
        "forma_pago": proveedor.forma_pago,
        "banco_codigo": proveedor.banco_codigo,
        "tipo_cuenta": proveedor.tipo_cuenta,
        "numero_cuenta": proveedor.numero_cuenta,
    }


def _asignar_referencias(pago: Pago) -> None:
    pago.referencia_16 = _campo_identificacion(pago)
    pago.referencia_11 = pago.numero_cuenta.strip()


def _campos_faltantes_pago(pago: Pago) -> list[str]:
    faltantes: list[str] = []
    if Decimal(pago.importe) <= 0:
        faltantes.append("importe")
    if not (pago.numero_factura and str(pago.numero_factura).strip()):
        faltantes.append("número de factura")
    if not (pago.concepto1 and str(pago.concepto1).strip()):
        faltantes.append("concepto")
    if not (pago.email_destino and str(pago.email_destino).strip()):
        faltantes.append("email destino")
    return faltantes


def _validar_pago_completo(pago: Pago) -> None:
    faltantes = _campos_faltantes_pago(pago)
    if faltantes:
        raise HTTPException(
            status_code=400,
            detail=f"Campos obligatorios faltantes: {', '.join(faltantes)}",
        )


def _recalcular_lote(db: Session, lote: LotePago) -> None:
    pagos = db.scalars(select(Pago).where(Pago.lote_id == lote.id, Pago.estado != "anulado")).all()
    lote.importe_total = sum((p.importe for p in pagos), Decimal("0.00"))
    lote.cantidad_pagos = len(pagos)


def _verificar_lote_editable(lote: LotePago) -> None:
    if lote.estado not in ("borrador", "confirmado"):
        raise HTTPException(
            status_code=400,
            detail=f"No se puede modificar un lote en estado '{lote.estado}'",
        )


def get_lote(db: Session, lote_id: int) -> LotePago:
    lote = db.scalar(
        select(LotePago)
        .options(joinedload(LotePago.pagos))
        .where(LotePago.id == lote_id)
    )
    if not lote:
        raise HTTPException(status_code=404, detail="Lote no encontrado")
    return lote


def list_lotes(
    db: Session,
    *,
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
    estado: str | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[LotePago], int]:
    stmt = select(LotePago).order_by(LotePago.fecha_operacion.desc(), LotePago.id.desc())
    if fecha_desde:
        stmt = stmt.where(LotePago.fecha_operacion >= fecha_desde)
    if fecha_hasta:
        stmt = stmt.where(LotePago.fecha_operacion <= fecha_hasta)
    if estado:
        stmt = stmt.where(LotePago.estado == estado)

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    page_size = min(max(page_size, 1), 100)
    offset = (max(page, 1) - 1) * page_size
    items = db.scalars(stmt.offset(offset).limit(page_size)).all()
    return list(items), total


def pages_count(total: int, page_size: int) -> int:
    return math.ceil(total / page_size) if total else 0


def crear_lote(db: Session, data: LoteCreate, usuario_id: int) -> LotePago:
    cuenta = db.get(CuentaOrdenante, data.cuenta_ordenante_id)
    if not cuenta or not cuenta.activa:
        raise HTTPException(status_code=400, detail="Cuenta ordenante inválida")

    lote = LotePago(
        fecha_operacion=data.fecha_operacion,
        fecha_limite=data.fecha_limite,
        cuenta_ordenante_id=data.cuenta_ordenante_id,
        concepto_general=data.concepto_general.strip(),
        usuario_id=usuario_id,
        estado="borrador",
    )
    db.add(lote)
    db.flush()

    for item in data.pagos:
        agregar_pago(db, lote.id, item)

    db.commit()
    return get_lote(db, lote.id)


def agregar_pago(db: Session, lote_id: int, item: PagoItemCreate) -> Pago:
    lote = get_lote(db, lote_id)
    _verificar_lote_editable(lote)

    proveedor = db.get(Proveedor, item.proveedor_id)
    if not proveedor or not proveedor.activo:
        raise HTTPException(status_code=400, detail=f"Proveedor {item.proveedor_id} no válido")

    snap = _snapshot_proveedor(proveedor)
    numero_factura = item.numero_factura
    cod_oficina = item.cod_oficina or proveedor.cod_oficina

    pago = Pago(
        lote_id=lote.id,
        proveedor_id=proveedor.id,
        importe=item.importe,
        cod_oficina=cod_oficina,
        fecha_limite=item.fecha_limite or lote.fecha_limite,
        concepto1=item.concepto1,
        concepto2=item.concepto2,
        concepto3=item.concepto3,
        concepto4=item.concepto4,
        numero_factura=numero_factura,
        estado="pendiente",
        **snap,
        email_destino=item.email_destino or proveedor.email,
    )
    db.add(pago)
    _validar_pago_completo(pago)
    _recalcular_lote(db, lote)
    db.commit()
    db.refresh(pago)
    return pago


def actualizar_pago(db: Session, pago_id: int, data: PagoItemUpdate) -> Pago:
    pago = db.get(Pago, pago_id)
    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    lote = get_lote(db, pago.lote_id)
    _verificar_lote_editable(lote)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(pago, key, value)

    _validar_pago_completo(pago)
    _recalcular_lote(db, lote)
    db.commit()
    db.refresh(pago)
    return pago


def eliminar_pago(db: Session, pago_id: int) -> None:
    pago = db.get(Pago, pago_id)
    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    lote = get_lote(db, pago.lote_id)
    _verificar_lote_editable(lote)
    pago.estado = "anulado"
    _recalcular_lote(db, lote)
    db.commit()


def actualizar_lote(db: Session, lote_id: int, data: LoteUpdate) -> LotePago:
    lote = get_lote(db, lote_id)
    _verificar_lote_editable(lote)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(lote, key, value)
    db.commit()
    return get_lote(db, lote_id)


def confirmar_lote(db: Session, lote_id: int) -> LotePago:
    lote = get_lote(db, lote_id)
    if lote.estado != "borrador":
        raise HTTPException(status_code=400, detail="Solo lotes en borrador se pueden confirmar")

    count = db.scalar(
        select(func.count(Pago.id)).where(
            Pago.lote_id == lote_id, Pago.estado != "anulado"
        )
    ) or 0
    if count == 0:
        raise HTTPException(status_code=400, detail="El lote no tiene pagos")

    lote.cantidad_pagos = count
    lote.estado = "confirmado"
    db.commit()
    return get_lote(db, lote_id)


def preparar_pagos_archivo(db: Session, lote: LotePago) -> list[Pago]:
    pagos = [
        p
        for p in lote.pagos
        if p.estado not in ("anulado",) and Decimal(p.importe) > 0
    ]
    if not pagos:
        raise HTTPException(status_code=400, detail="No hay pagos válidos para procesar")

    incompletos = [
        p.razon_social
        for p in pagos
        if _campos_faltantes_pago(p)
    ]
    if incompletos:
        nombres = ", ".join(incompletos[:5])
        extra = f" y {len(incompletos) - 5} más" if len(incompletos) > 5 else ""
        raise HTTPException(
            status_code=400,
            detail=(
                f"No se puede procesar: {len(incompletos)} pago(s) con datos incompletos "
                f"(factura, concepto o email). Revise: {nombres}{extra}"
            ),
        )

    for pago in pagos:
        _asignar_referencias(pago)
        pago.estado = "incluido_archivo"
        build_payment_line(pago, concepto=lote.concepto_general, ciudad="BOGOTA")

    return pagos
