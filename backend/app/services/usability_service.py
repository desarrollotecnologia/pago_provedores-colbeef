"""Persistencia y agregación de eventos de usabilidad."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models import EventoUsabilidad

MAX_EVENTS = 50_000
RETENTION_DAYS = 90

ALLOWED_ACTIONS = {
    "session_start",
    "module_open",
    "action_complete",
    "error_ui",
    "admin_open",
}


def _now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def _cleanup_old_events(db: Session) -> None:
    cutoff = _now() - timedelta(days=RETENTION_DAYS)
    db.execute(delete(EventoUsabilidad).where(EventoUsabilidad.timestamp < cutoff))

    total = db.scalar(select(func.count()).select_from(EventoUsabilidad)) or 0
    if total > MAX_EVENTS:
        excess = total - MAX_EVENTS
        ids_subq = (
            select(EventoUsabilidad.id)
            .order_by(EventoUsabilidad.timestamp.asc())
            .limit(excess)
            .scalar_subquery()
        )
        db.execute(delete(EventoUsabilidad).where(EventoUsabilidad.id.in_(ids_subq)))


def registrar_evento(
    db: Session,
    *,
    usuario: str,
    session_id: str,
    action: str,
    module: str,
    detail: str | None = None,
    page: str | None = None,
    meta: dict | None = None,
    timestamp: datetime | None = None,
) -> EventoUsabilidad:
    if action not in ALLOWED_ACTIONS:
        action = "action_complete"

    usuario_safe = (usuario or "anonimo")[:80]
    session_safe = (session_id or "unknown")[:64]
    module_safe = (module or "general")[:60]
    detail_safe = (detail or "")[:255] or None
    page_safe = (page or "")[:200] or None

    if meta:
        meta = {k: v for k, v in meta.items() if k not in ("password", "token", "secret")}

    evento = EventoUsabilidad(
        timestamp=timestamp or _now(),
        usuario=usuario_safe,
        session_id=session_safe,
        action=action[:40],
        module=module_safe,
        detail=detail_safe,
        page=page_safe,
        meta=meta,
    )
    db.add(evento)
    db.flush()
    _cleanup_old_events(db)
    db.commit()
    db.refresh(evento)
    return evento


def obtener_estadisticas(db: Session, *, days: int = 30, solo_admin: bool = False) -> dict:
    days = min(max(days, 1), 90)
    since = _now() - timedelta(days=days)

    filtro_admin = None
    if solo_admin:
        from app.models import Usuario

        filtro_admin = list(
            db.scalars(select(Usuario.username).where(Usuario.rol == "admin")).all()
        )
        if not filtro_admin:
            filtro_admin = ["__none__"]

    def _base_filter(stmt):
        stmt = stmt.where(EventoUsabilidad.timestamp >= since)
        if filtro_admin is not None:
            stmt = stmt.where(EventoUsabilidad.usuario.in_(filtro_admin))
        return stmt

    total_eventos = db.scalar(
        select(func.count()).select_from(
            _base_filter(select(EventoUsabilidad)).subquery()
        )
    ) or 0

    usuarios_unicos = db.scalar(
        _base_filter(select(func.count(func.distinct(EventoUsabilidad.usuario))))
    ) or 0

    sesiones_unicas = db.scalar(
        _base_filter(select(func.count(func.distinct(EventoUsabilidad.session_id))))
    ) or 0

    ultimo = db.scalar(
        _base_filter(select(EventoUsabilidad))
        .order_by(EventoUsabilidad.timestamp.desc())
        .limit(1)
    )

    eventos_por_dia = db.execute(
        _base_filter(
            select(
                func.date(EventoUsabilidad.timestamp).label("dia"),
                func.count().label("total"),
            )
        )
        .group_by(func.date(EventoUsabilidad.timestamp))
        .order_by(func.date(EventoUsabilidad.timestamp))
    ).all()

    top_usuarios = db.execute(
        _base_filter(
            select(EventoUsabilidad.usuario, func.count().label("total"))
        )
        .group_by(EventoUsabilidad.usuario)
        .order_by(func.count().desc())
        .limit(10)
    ).all()

    por_modulo = db.execute(
        _base_filter(select(EventoUsabilidad.module, func.count().label("total")))
        .group_by(EventoUsabilidad.module)
        .order_by(func.count().desc())
    ).all()

    por_accion = db.execute(
        _base_filter(select(EventoUsabilidad.action, func.count().label("total")))
        .group_by(EventoUsabilidad.action)
        .order_by(func.count().desc())
    ).all()

    recientes = db.scalars(
        _base_filter(select(EventoUsabilidad))
        .order_by(EventoUsabilidad.timestamp.desc())
        .limit(150)
    ).all()

    return {
        "periodo_dias": days,
        "desde": since.isoformat(),
        "kpis": {
            "total_eventos": total_eventos,
            "usuarios_unicos": usuarios_unicos,
            "sesiones_unicas": sesiones_unicas,
            "ultima_actividad": {
                "usuario": ultimo.usuario if ultimo else None,
                "action": ultimo.action if ultimo else None,
                "module": ultimo.module if ultimo else None,
                "detail": ultimo.detail if ultimo else None,
                "timestamp": ultimo.timestamp.isoformat() if ultimo else None,
            },
        },
        "eventos_por_dia": [{"dia": str(r.dia), "total": r.total} for r in eventos_por_dia],
        "top_usuarios": [{"usuario": r.usuario, "total": r.total} for r in top_usuarios],
        "por_modulo": [{"module": r.module, "total": r.total} for r in por_modulo],
        "por_accion": [{"action": r.action, "total": r.total} for r in por_accion],
        "recientes": [
            {
                "timestamp": e.timestamp.isoformat(),
                "usuario": e.usuario,
                "action": e.action,
                "module": e.module,
                "detail": e.detail,
                "page": e.page,
            }
            for e in recientes
        ],
    }
