from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.core.database import get_db
from app.models import Usuario
from app.schemas.common import MessageResponse
from app.schemas.historial import HistorialPagoDetalle, HistorialPagosResponse
from app.schemas.lotes import (
    LoteCreate,
    LoteListItem,
    LoteListResponse,
    LoteResponse,
    LoteUpdate,
    PagoItemCreate,
    PagoItemUpdate,
    PagoResponse,
    ProcesarLoteResponse,
)
from app.services import historial_service, lote_service as svc
from app.services.archivo_plano_service import generar_archivo_plano
from app.services.config_service import get_ciudad_default
from app.services.email_service import enviar_correos_lote

router = APIRouter(prefix="/lotes", tags=["Lotes de pago"])


def _generar_archivo_interno(db: Session, lote_id: int) -> ProcesarLoteResponse:
    lote = svc.get_lote(db, lote_id)
    if lote.estado == "borrador":
        lote = svc.confirmar_lote(db, lote_id)

    pagos = svc.preparar_pagos_archivo(db, lote)
    ciudad = get_ciudad_default(db)
    ruta, nombre = generar_archivo_plano(
        pagos, concepto_general=lote.concepto_general, ciudad=ciudad
    )
    lote.archivo_plano_nombre = nombre
    lote.archivo_plano_ruta = str(ruta)
    lote.estado = "archivo_generado"
    db.commit()

    return ProcesarLoteResponse(
        lote_id=lote.id,
        archivo=nombre,
        ruta=str(ruta),
        lineas=len(pagos),
        mensaje="Archivo plano generado correctamente",
    )


@router.get("", response_model=LoteListResponse)
def listar_lotes(
    fecha_desde: date | None = Query(None),
    fecha_hasta: date | None = Query(None),
    estado: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    items, total = svc.list_lotes(
        db,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        estado=estado,
        page=page,
        page_size=page_size,
    )
    return LoteListResponse(
        items=[LoteListItem.model_validate(i) for i in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=svc.pages_count(total, page_size),
    )


@router.post("", response_model=LoteResponse, status_code=status.HTTP_201_CREATED)
def crear_lote(
    payload: LoteCreate,
    db: Session = Depends(get_db),
    user: Usuario = Depends(require_admin),
):
    return svc.crear_lote(db, payload, user.id)


@router.get("/historial/pagos", response_model=HistorialPagosResponse)
def historial_pagos_por_fecha(
    fecha: date = Query(..., description="Fecha de operación del lote (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    q: str | None = Query(None, max_length=80),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return historial_service.buscar_pagos_por_fecha(
        db, fecha=fecha, page=page, page_size=page_size, q=q
    )


@router.get("/historial/pagos/{pago_id}", response_model=HistorialPagoDetalle)
def historial_pago_detalle(
    pago_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    detalle = historial_service.obtener_pago_detalle(db, pago_id)
    if not detalle:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Pago no encontrado")
    return detalle


@router.get("/{lote_id}", response_model=LoteResponse)
def obtener_lote(
    lote_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return svc.get_lote(db, lote_id)


@router.put("/{lote_id}", response_model=LoteResponse)
def actualizar_lote(
    lote_id: int,
    payload: LoteUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return svc.actualizar_lote(db, lote_id, payload)


@router.post("/{lote_id}/confirmar", response_model=LoteResponse)
def confirmar_lote(
    lote_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return svc.confirmar_lote(db, lote_id)


@router.post("/{lote_id}/pagos", response_model=PagoResponse, status_code=status.HTTP_201_CREATED)
def agregar_pago(
    lote_id: int,
    payload: PagoItemCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return svc.agregar_pago(db, lote_id, payload)


@router.put("/pagos/{pago_id}", response_model=PagoResponse)
def actualizar_pago(
    pago_id: int,
    payload: PagoItemUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return svc.actualizar_pago(db, pago_id, payload)


@router.delete("/pagos/{pago_id}", response_model=MessageResponse)
def eliminar_pago(
    pago_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    svc.eliminar_pago(db, pago_id)
    return MessageResponse(message="Pago eliminado del lote")


@router.post("/{lote_id}/generar-archivo", response_model=ProcesarLoteResponse)
def generar_archivo(
    lote_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    return _generar_archivo_interno(db, lote_id)


@router.get("/{lote_id}/descargar-archivo")
def descargar_archivo(
    lote_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    lote = svc.get_lote(db, lote_id)
    if not lote.archivo_plano_ruta:
        raise HTTPException(status_code=404, detail="Archivo no generado")
    return FileResponse(
        lote.archivo_plano_ruta,
        filename=lote.archivo_plano_nombre or "pagos.txt",
        media_type="text/plain",
    )


@router.post("/{lote_id}/enviar-correos", response_model=ProcesarLoteResponse)
def enviar_correos(
    lote_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    lote = svc.get_lote(db, lote_id)
    if lote.estado not in ("archivo_generado", "completado", "confirmado"):
        if lote.estado == "correos_enviados":
            raise HTTPException(
                status_code=400,
                detail="Los correos de este lote ya fueron enviados. No se permiten reenvíos.",
            )
        raise HTTPException(
            status_code=400,
            detail="Primero genere el archivo plano antes de enviar correos",
        )
    try:
        enviados, errores, omitidos = enviar_correos_lote(db, lote)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()

    return ProcesarLoteResponse(
        lote_id=lote.id,
        archivo=lote.archivo_plano_nombre or "",
        ruta=lote.archivo_plano_ruta or "",
        lineas=lote.cantidad_pagos,
        correos_enviados=enviados,
        correos_error=errores,
        mensaje=f"Correos enviados: {enviados}, errores: {errores}"
        + (f", omitidos (ya enviados): {omitidos}" if omitidos else ""),
    )


@router.post("/{lote_id}/procesar", response_model=ProcesarLoteResponse)
def procesar_lote_completo(
    lote_id: int,
    enviar_correos: bool = Query(True),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_admin),
):
    gen = _generar_archivo_interno(db, lote_id)
    if not enviar_correos:
        return gen

    lote = svc.get_lote(db, lote_id)
    try:
        enviados, errores, omitidos = enviar_correos_lote(db, lote)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    db.commit()

    extra = f", omitidos: {omitidos}" if omitidos else ""
    return ProcesarLoteResponse(
        lote_id=lote_id,
        archivo=gen.archivo,
        ruta=gen.ruta,
        lineas=gen.lineas,
        correos_enviados=enviados,
        correos_error=errores,
        mensaje=f"{gen.mensaje} | Correos: {enviados} enviados, {errores} errores{extra}",
    )
