"""Métricas y estadísticas del dashboard."""
from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.timezone import today_colombia
from app.models import LotePago, Pago, Proveedor
from app.schemas.dashboard import DashboardResumen, DashboardResponse, TopProveedor


def obtener_dashboard(
    db: Session,
    *,
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
) -> DashboardResponse:
    if not fecha_hasta:
        fecha_hasta = today_colombia()
    if not fecha_desde:
        fecha_desde = fecha_hasta

    filtros = [
        LotePago.fecha_operacion >= fecha_desde,
        LotePago.fecha_operacion <= fecha_hasta,
        Pago.estado != "anulado",
        LotePago.estado != "anulado",
    ]

    importe_total = db.scalar(
        select(func.coalesce(func.sum(Pago.importe), 0))
        .join(LotePago, Pago.lote_id == LotePago.id)
        .where(*filtros)
    ) or Decimal("0")

    cantidad_pagos = db.scalar(
        select(func.count(Pago.id)).join(LotePago, Pago.lote_id == LotePago.id).where(*filtros)
    ) or 0

    cantidad_proveedores = db.scalar(
        select(func.count(func.distinct(Pago.proveedor_id)))
        .join(LotePago, Pago.lote_id == LotePago.id)
        .where(*filtros)
    ) or 0

    cantidad_lotes = db.scalar(
        select(func.count(LotePago.id)).where(
            LotePago.fecha_operacion >= fecha_desde,
            LotePago.fecha_operacion <= fecha_hasta,
            LotePago.estado != "anulado",
        )
    ) or 0

    top_rows = db.execute(
        select(
            Pago.proveedor_id,
            Proveedor.razon_social,
            func.sum(Pago.importe).label("total"),
            func.count(Pago.id).label("cnt"),
        )
        .join(LotePago, Pago.lote_id == LotePago.id)
        .join(Proveedor, Proveedor.id == Pago.proveedor_id)
        .where(
            LotePago.fecha_operacion >= fecha_desde,
            LotePago.fecha_operacion <= fecha_hasta,
            Pago.estado != "anulado",
            LotePago.estado != "anulado",
        )
        .group_by(Pago.proveedor_id, Proveedor.razon_social)
        .order_by(func.sum(Pago.importe).desc())
        .limit(10)
    ).all()

    ultimos = db.scalars(
        select(LotePago)
        .where(
            LotePago.estado != "anulado",
            LotePago.fecha_operacion >= fecha_desde,
            LotePago.fecha_operacion <= fecha_hasta,
        )
        .order_by(LotePago.id.desc())
        .limit(5)
    ).all()

    return DashboardResponse(
        resumen=DashboardResumen(
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            importe_total=Decimal(importe_total),
            cantidad_proveedores=cantidad_proveedores,
            cantidad_lotes=cantidad_lotes,
            cantidad_pagos=cantidad_pagos,
        ),
        top_proveedores=[
            TopProveedor(
                proveedor_id=r.proveedor_id,
                razon_social=r.razon_social,
                total_pagado=Decimal(r.total),
                cantidad_pagos=r.cnt,
            )
            for r in top_rows
        ],
        ultimos_lotes=[
            {
                "id": l.id,
                "fecha_operacion": l.fecha_operacion.isoformat(),
                "estado": l.estado,
                "importe_total": str(l.importe_total),
                "cantidad_pagos": l.cantidad_pagos,
                "concepto": l.concepto_general,
            }
            for l in ultimos
        ],
    )
