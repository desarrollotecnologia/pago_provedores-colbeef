"""Consulta de pagos históricos por fecha de operación del lote."""
import math
from datetime import date
from decimal import Decimal

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import Banco, LotePago, Pago
from app.schemas.historial import (
    HistorialPagoDetalle,
    HistorialPagoItem,
    HistorialPagosResponse,
    HistorialResumen,
)


def _filtros_fecha(fecha: date, q: str | None = None):
    filtros = [
        LotePago.fecha_operacion == fecha,
        Pago.estado != "anulado",
        LotePago.estado != "anulado",
    ]
    if q:
        term = f"%{q.strip()}%"
        filtros.append(
            or_(
                Pago.razon_social.ilike(term),
                Pago.identificacion.ilike(term),
                Pago.numero_factura.ilike(term),
            )
        )
    return filtros


def buscar_pagos_por_fecha(
    db: Session,
    *,
    fecha: date,
    page: int = 1,
    page_size: int = 50,
    q: str | None = None,
) -> HistorialPagosResponse:
    filtros = _filtros_fecha(fecha, q)

    total = (
        db.scalar(
            select(func.count(Pago.id))
            .join(LotePago, Pago.lote_id == LotePago.id)
            .where(*filtros)
        )
        or 0
    )
    page_size = min(max(page_size, 1), 100)
    page = max(page, 1)
    offset = (page - 1) * page_size
    pages = math.ceil(total / page_size) if total else 0

    importe_total = db.scalar(
        select(func.coalesce(func.sum(Pago.importe), 0))
        .join(LotePago, Pago.lote_id == LotePago.id)
        .where(*filtros)
    ) or Decimal("0")

    rows = db.execute(
        select(Pago, LotePago)
        .join(LotePago, Pago.lote_id == LotePago.id)
        .where(*filtros)
        .order_by(LotePago.id.desc(), Pago.id.desc())
        .offset(offset)
        .limit(page_size)
    ).all()

    items = [
        HistorialPagoItem(
            id=pago.id,
            lote_id=lote.id,
            lote_fecha_operacion=lote.fecha_operacion,
            lote_concepto=lote.concepto_general,
            lote_estado=lote.estado,
            proveedor_id=pago.proveedor_id,
            razon_social=pago.razon_social,
            identificacion=pago.identificacion,
            importe=pago.importe,
            numero_factura=pago.numero_factura,
            concepto1=pago.concepto1,
            estado=pago.estado,
            email_destino=pago.email_destino,
        )
        for pago, lote in rows
    ]

    return HistorialPagosResponse(
        resumen=HistorialResumen(
            fecha=fecha,
            importe_total=Decimal(importe_total),
            cantidad_pagos=total,
        ),
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


def obtener_pago_detalle(db: Session, pago_id: int) -> HistorialPagoDetalle | None:
    row = db.execute(
        select(Pago, LotePago, Banco.descripcion)
        .join(LotePago, Pago.lote_id == LotePago.id)
        .outerjoin(Banco, Banco.codigo == Pago.banco_codigo)
        .where(Pago.id == pago_id, Pago.estado != "anulado", LotePago.estado != "anulado")
    ).first()
    if not row:
        return None
    pago, lote, banco_desc = row
    return HistorialPagoDetalle(
        id=pago.id,
        lote_id=lote.id,
        lote_fecha_operacion=lote.fecha_operacion,
        lote_fecha_limite=lote.fecha_limite,
        lote_concepto=lote.concepto_general,
        lote_estado=lote.estado,
        lote_importe_total=lote.importe_total,
        lote_archivo=lote.archivo_plano_nombre,
        proveedor_id=pago.proveedor_id,
        identificacion=pago.identificacion,
        tipo_identificacion=pago.tipo_identificacion,
        digito_verificacion=pago.digito_verificacion,
        razon_social=pago.razon_social,
        banco_codigo=pago.banco_codigo,
        banco_descripcion=banco_desc,
        tipo_cuenta=pago.tipo_cuenta,
        numero_cuenta=pago.numero_cuenta,
        cod_oficina=pago.cod_oficina,
        forma_pago=pago.forma_pago,
        importe=pago.importe,
        fecha_limite=pago.fecha_limite,
        concepto1=pago.concepto1,
        concepto2=pago.concepto2,
        concepto3=pago.concepto3,
        concepto4=pago.concepto4,
        numero_factura=pago.numero_factura,
        email_destino=pago.email_destino,
        referencia_16=pago.referencia_16,
        referencia_11=pago.referencia_11,
        estado=pago.estado,
    )
