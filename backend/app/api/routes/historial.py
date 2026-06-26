from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.database import get_db
from app.models import Usuario
from app.schemas.historial import HistorialPagoDetalle, HistorialPagosResponse
from app.services import historial_service as svc

router = APIRouter(prefix="/historial", tags=["Historial de pagos"])


@router.get("/pagos", response_model=HistorialPagosResponse)
def listar_pagos_por_fecha(
    fecha: date = Query(..., description="Fecha de operación del lote (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    q: str | None = Query(None, max_length=80, description="Buscar por proveedor, NIT o factura"),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return svc.buscar_pagos_por_fecha(db, fecha=fecha, page=page, page_size=page_size, q=q)


@router.get("/pagos/{pago_id}", response_model=HistorialPagoDetalle)
def detalle_pago(
    pago_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    detalle = svc.obtener_pago_detalle(db, pago_id)
    if not detalle:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Pago no encontrado")
    return detalle
