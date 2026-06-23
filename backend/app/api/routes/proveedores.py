from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.core.database import get_db
from app.models import Usuario
from app.schemas.common import MessageResponse
from app.schemas.proveedores import (
    ProveedorCreate,
    ProveedorListResponse,
    ProveedorResponse,
    ProveedorUpdate,
)
from app.services import proveedor_service as svc

router = APIRouter(prefix="/proveedores", tags=["Proveedores"])


@router.get("", response_model=ProveedorListResponse)
def listar_proveedores(
    q: str | None = Query(None, description="Buscar por nombre, identificación o cuenta"),
    banco_codigo: int | None = Query(None),
    activo: bool | None = Query(True),
    fecha_desde: date | None = Query(None, description="Filtrar proveedores pagados desde"),
    fecha_hasta: date | None = Query(None, description="Filtrar proveedores pagados hasta"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    items, total = svc.list_proveedores(
        db,
        q=q,
        banco_codigo=banco_codigo,
        activo=activo,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        page=page,
        page_size=page_size,
    )
    return ProveedorListResponse(
        items=[ProveedorResponse.model_validate(p) for p in items],
        total=total,
        page=page,
        page_size=page_size,
        pages=svc.pages_count(total, page_size),
    )


@router.get("/{proveedor_id}", response_model=ProveedorResponse)
def obtener_proveedor(
    proveedor_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return svc.get_proveedor(db, proveedor_id)


@router.post("", response_model=ProveedorResponse, status_code=status.HTTP_201_CREATED)
def crear_proveedor(
    payload: ProveedorCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return svc.create_proveedor(db, payload)


@router.put("/{proveedor_id}", response_model=ProveedorResponse)
def actualizar_proveedor(
    proveedor_id: int,
    payload: ProveedorUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return svc.update_proveedor(db, proveedor_id, payload)


@router.delete("/{proveedor_id}", response_model=MessageResponse)
def desactivar_proveedor(
    proveedor_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_admin),
):
    svc.deactivate_proveedor(db, proveedor_id)
    return MessageResponse(message=f"Proveedor {proveedor_id} desactivado")
