from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_operador
from app.core.database import get_db
from app.models import Usuario
from app.schemas.usability import UsabilityEventIn, UsabilityEventOut, UsabilityStatsResponse
from app.services import usability_service as svc

router = APIRouter(prefix="/usability", tags=["Usabilidad"])


@router.post("/event", response_model=UsabilityEventOut)
def registrar_evento(
    payload: UsabilityEventIn,
    db: Session = Depends(get_db),
    user: Usuario = Depends(get_current_user),
):
    """
    Registra un evento de usabilidad. Requiere sesión activa.
    El usuario se toma del token JWT (no del body) por seguridad.
    """
    evento = svc.registrar_evento(
        db,
        usuario=user.username,
        session_id=payload.session_id,
        action=payload.action,
        module=payload.module,
        detail=payload.detail,
        page=payload.page,
        meta=payload.meta,
        timestamp=payload.timestamp,
    )
    return UsabilityEventOut(id=evento.id, message="Evento registrado")


@router.get("/stats", response_model=UsabilityStatsResponse)
def estadisticas_usabilidad(
    days: int = Query(30, ge=7, le=90),
    db: Session = Depends(get_db),
    _: Usuario = Depends(require_operador),
):
    """Estadísticas de uso del administrador — solo usuario panel (operador)."""
    return svc.obtener_estadisticas(db, days=days, solo_admin=True)
