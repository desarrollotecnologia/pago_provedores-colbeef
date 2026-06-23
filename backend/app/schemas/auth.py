from datetime import datetime

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    usuario: str = Field(..., min_length=1, description="Username o nombre completo")
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    usuario: "UsuarioAuth"


class UsuarioAuth(BaseModel):
    id: int
    username: str
    nombre_completo: str
    rol: str

    model_config = {"from_attributes": True}


class UsuarioMe(BaseModel):
    id: int
    username: str
    nombre_completo: str
    rol: str
    activo: bool
    ultimo_acceso: datetime | None
    creado_en: datetime

    model_config = {"from_attributes": True}
