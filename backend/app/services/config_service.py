"""Acceso a configuración SMTP y general (env + BD)."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import Configuracion


def _get_db_config(db: Session, clave: str) -> str | None:
    row = db.scalar(select(Configuracion).where(Configuracion.clave == clave))
    return row.valor if row else None


def get_smtp_config(db: Session) -> dict:
    settings = get_settings()
    return {
        "host": settings.smtp_host or _get_db_config(db, "smtp_host") or "",
        "port": int(_get_db_config(db, "smtp_port") or settings.smtp_port),
        "user": settings.smtp_user or _get_db_config(db, "smtp_user") or "",
        "password": settings.smtp_password or _get_db_config(db, "smtp_password") or "",
        "from_email": settings.smtp_from_email or _get_db_config(db, "smtp_user") or "",
        "from_name": settings.smtp_from_name or _get_db_config(db, "smtp_from_name") or "",
        "use_tls": settings.smtp_use_tls,
    }


def get_ciudad_default(db: Session) -> str:
    settings = get_settings()
    return _get_db_config(db, "ciudad_default") or settings.ciudad_default


def get_campo_factura(db: Session) -> str:
    return _get_db_config(db, "concepto_campo_factura") or "concepto1"
