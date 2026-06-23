import math
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models import Banco, LotePago, Pago, Proveedor, TipoCuenta, TipoIdentificacion
from app.schemas.proveedores import ProveedorCreate, ProveedorUpdate


def _validate_catalog_refs(db: Session, data: dict) -> None:
    if "tipo_identificacion" in data:
        tipo = db.get(TipoIdentificacion, data["tipo_identificacion"])
        if not tipo:
            raise HTTPException(status_code=400, detail="Tipo de identificación inválido")

    if "tipo_cuenta" in data:
        tipo = db.get(TipoCuenta, data["tipo_cuenta"])
        if not tipo:
            raise HTTPException(status_code=400, detail="Tipo de cuenta inválido")

    if "banco_codigo" in data:
        banco = db.get(Banco, data["banco_codigo"])
        if not banco or not banco.activo:
            raise HTTPException(status_code=400, detail="Banco inválido")


def _check_duplicate(
    db: Session,
    identificacion: str,
    tipo_identificacion: int,
    exclude_id: int | None = None,
) -> None:
    stmt = select(Proveedor).where(
        Proveedor.identificacion == identificacion,
        Proveedor.tipo_identificacion == tipo_identificacion,
    )
    if exclude_id:
        stmt = stmt.where(Proveedor.id != exclude_id)

    if db.scalar(stmt):
        raise HTTPException(
            status_code=409,
            detail="Ya existe un proveedor con esa identificación y tipo",
        )


def list_proveedores(
    db: Session,
    *,
    q: str | None = None,
    banco_codigo: int | None = None,
    activo: bool | None = True,
    fecha_desde: date | None = None,
    fecha_hasta: date | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Proveedor], int]:
    stmt = select(Proveedor).options(joinedload(Proveedor.banco))

    if activo is not None:
        stmt = stmt.where(Proveedor.activo.is_(activo))

    if q:
        term = f"%{q.strip().upper()}%"
        stmt = stmt.where(
            or_(
                Proveedor.razon_social.like(term),
                Proveedor.identificacion.like(f"%{q.strip()}%"),
                Proveedor.numero_cuenta.like(f"%{q.strip()}%"),
            )
        )

    if banco_codigo:
        stmt = stmt.where(Proveedor.banco_codigo == banco_codigo)

    if fecha_desde or fecha_hasta:
        pago_subq = select(Pago.proveedor_id).join(LotePago, Pago.lote_id == LotePago.id)
        if fecha_desde:
            pago_subq = pago_subq.where(LotePago.fecha_operacion >= fecha_desde)
        if fecha_hasta:
            pago_subq = pago_subq.where(LotePago.fecha_operacion <= fecha_hasta)
        pago_subq = pago_subq.distinct()
        stmt = stmt.where(Proveedor.id.in_(pago_subq))

    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.scalar(count_stmt) or 0

    page = max(page, 1)
    page_size = min(max(page_size, 1), 100)
    offset = (page - 1) * page_size

    items = db.scalars(
        stmt.order_by(Proveedor.razon_social).offset(offset).limit(page_size)
    ).unique().all()

    return list(items), total


def get_proveedor(db: Session, proveedor_id: int) -> Proveedor:
    proveedor = db.scalar(
        select(Proveedor)
        .options(joinedload(Proveedor.banco))
        .where(Proveedor.id == proveedor_id)
    )
    if not proveedor:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado")
    return proveedor


def create_proveedor(db: Session, data: ProveedorCreate) -> Proveedor:
    payload = data.model_dump()
    if payload.get("email") == "":
        payload["email"] = None

    _validate_catalog_refs(db, payload)
    _check_duplicate(db, payload["identificacion"], payload["tipo_identificacion"])

    proveedor = Proveedor(**payload, activo=True)
    db.add(proveedor)
    db.commit()
    db.refresh(proveedor)
    return get_proveedor(db, proveedor.id)


def update_proveedor(
    db: Session, proveedor_id: int, data: ProveedorUpdate
) -> Proveedor:
    proveedor = get_proveedor(db, proveedor_id)
    updates = data.model_dump(exclude_unset=True)

    if "email" in updates and updates["email"] == "":
        updates["email"] = None

    _validate_catalog_refs(db, updates)

    identificacion = updates.get("identificacion", proveedor.identificacion)
    tipo_id = updates.get("tipo_identificacion", proveedor.tipo_identificacion)
    if "identificacion" in updates or "tipo_identificacion" in updates:
        _check_duplicate(db, identificacion, tipo_id, exclude_id=proveedor_id)

    for key, value in updates.items():
        setattr(proveedor, key, value)

    db.commit()
    return get_proveedor(db, proveedor_id)


def deactivate_proveedor(db: Session, proveedor_id: int) -> Proveedor:
    proveedor = get_proveedor(db, proveedor_id)
    proveedor.activo = False
    db.commit()
    return get_proveedor(db, proveedor_id)


def pages_count(total: int, page_size: int) -> int:
    if total == 0:
        return 0
    return math.ceil(total / page_size)
