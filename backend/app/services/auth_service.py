from datetime import UTC, datetime

from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import normalizar_nombre
from app.core.config import get_settings
from app.core.security import create_access_token, verify_password
from app.models import Usuario
from app.schemas.auth import TokenResponse, UsuarioAuth


def authenticate_user(db: Session, usuario: str, password: str) -> Usuario:
    identificador = usuario.strip()
    nombre_norm = normalizar_nombre(identificador)

    stmt = select(Usuario).where(
        Usuario.activo.is_(True),
        or_(
            func.lower(Usuario.username) == identificador.lower(),
            Usuario.nombre_normalizado == nombre_norm,
        ),
    )
    user = db.scalar(stmt)

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
        )

    user.ultimo_acceso = datetime.now(UTC).replace(tzinfo=None)
    db.commit()
    db.refresh(user)
    return user


def build_token_response(user: Usuario) -> TokenResponse:
    settings = get_settings()
    token = create_access_token(
        user_id=user.id,
        username=user.username,
        rol=user.rol,
    )
    return TokenResponse(
        access_token=token,
        expires_in=settings.access_token_expire_minutes * 60,
        usuario=UsuarioAuth.model_validate(user),
    )
