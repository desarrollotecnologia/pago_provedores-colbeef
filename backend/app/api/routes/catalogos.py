from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Banco, TipoCuenta, TipoIdentificacion, Usuario
from app.schemas.common import BancoCatalogo, CatalogoItem

router = APIRouter(prefix="/catalogos", tags=["Catálogos"])


@router.get("/bancos", response_model=list[BancoCatalogo])
def listar_bancos(
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    stmt = select(Banco).where(Banco.activo.is_(True)).order_by(Banco.descripcion)
    return db.scalars(stmt).all()


@router.get("/tipos-identificacion", response_model=list[CatalogoItem])
def listar_tipos_identificacion(
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return db.scalars(select(TipoIdentificacion).order_by(TipoIdentificacion.codigo)).all()


@router.get("/tipos-cuenta", response_model=list[CatalogoItem])
def listar_tipos_cuenta(
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_user),
):
    return db.scalars(select(TipoCuenta).order_by(TipoCuenta.codigo)).all()
