from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Usuario
from app.schemas.auth import LoginRequest, TokenResponse, UsuarioMe
from app.services.auth_service import authenticate_user, build_token_response

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    Iniciar sesión con username o nombre completo (sin importar mayúsculas).
    Ejemplos: `viviana`, `VIVIANA ANDREA`, `panel`
    """
    user = authenticate_user(db, payload.usuario, payload.password)
    return build_token_response(user)


@router.get("/me", response_model=UsuarioMe)
def me(current_user: Usuario = Depends(get_current_user)):
    return current_user
