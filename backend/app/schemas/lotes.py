from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class PagoItemCreate(BaseModel):
    proveedor_id: int
    importe: Decimal = Field(..., ge=0, decimal_places=2)
    cod_oficina: str | None = None
    fecha_limite: date | None = None
    concepto1: str | None = None
    concepto2: str | None = None
    concepto3: str | None = None
    concepto4: str | None = None
    numero_factura: str | None = None
    email_destino: str | None = None

    @field_validator("numero_factura", mode="before")
    @classmethod
    def factura_from_concepto(cls, v, info):
        if v:
            return str(v).strip()
        return v


class LoteCreate(BaseModel):
    fecha_operacion: date
    cuenta_ordenante_id: int
    concepto_general: str = Field(..., min_length=1, max_length=120)
    fecha_limite: date | None = None
    pagos: list[PagoItemCreate] = Field(default_factory=list)


class LoteUpdate(BaseModel):
    concepto_general: str | None = Field(None, max_length=120)
    fecha_limite: date | None = None
    cuenta_ordenante_id: int | None = None


class PagoItemUpdate(BaseModel):
    importe: Decimal | None = Field(None, gt=0)
    cod_oficina: str | None = None
    fecha_limite: date | None = None
    concepto1: str | None = None
    concepto2: str | None = None
    concepto3: str | None = None
    concepto4: str | None = None
    numero_factura: str | None = None
    email_destino: str | None = None


class PagoResponse(BaseModel):
    id: int
    proveedor_id: int
    identificacion: str
    tipo_identificacion: int
    digito_verificacion: int | None
    razon_social: str
    banco_codigo: int
    tipo_cuenta: int
    numero_cuenta: str
    cod_oficina: str | None
    forma_pago: int
    importe: Decimal
    fecha_limite: date | None
    concepto1: str | None
    concepto2: str | None
    concepto3: str | None
    concepto4: str | None
    numero_factura: str | None
    email_destino: str | None
    referencia_16: str | None
    referencia_11: str | None
    estado: str

    model_config = {"from_attributes": True}


class LoteResponse(BaseModel):
    id: int
    fecha_operacion: date
    fecha_limite: date | None
    cuenta_ordenante_id: int
    concepto_general: str
    estado: str
    importe_total: Decimal
    cantidad_pagos: int
    archivo_plano_nombre: str | None
    usuario_id: int
    creado_en: datetime
    pagos: list[PagoResponse] = []

    model_config = {"from_attributes": True}


class LoteListItem(BaseModel):
    id: int
    fecha_operacion: date
    concepto_general: str
    estado: str
    importe_total: Decimal
    cantidad_pagos: int
    archivo_plano_nombre: str | None
    creado_en: datetime

    model_config = {"from_attributes": True}


class LoteListResponse(BaseModel):
    items: list[LoteListItem]
    total: int
    page: int
    page_size: int
    pages: int


class ProcesarLoteResponse(BaseModel):
    lote_id: int
    archivo: str
    ruta: str
    lineas: int
    correos_enviados: int = 0
    correos_error: int = 0
    mensaje: str
