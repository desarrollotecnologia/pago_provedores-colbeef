from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class UsabilityEventIn(BaseModel):
    timestamp: datetime | None = None
    session_id: str = Field(..., min_length=1, max_length=64)
    action: str = Field(..., min_length=1, max_length=40)
    module: str = Field(..., min_length=1, max_length=60)
    detail: str | None = Field(None, max_length=255)
    page: str | None = Field(None, max_length=200)
    meta: dict | None = None

    @field_validator("detail", "page", mode="before")
    @classmethod
    def strip_optional(cls, v):
        if isinstance(v, str):
            v = v.strip()
            return v or None
        return v


class UsabilityEventOut(BaseModel):
    id: int
    message: str = "Evento registrado"

    model_config = {"from_attributes": True}


class UsabilityStatsResponse(BaseModel):
    periodo_dias: int
    desde: str
    kpis: dict
    eventos_por_dia: list[dict]
    top_usuarios: list[dict]
    por_modulo: list[dict]
    por_accion: list[dict]
    recientes: list[dict]
