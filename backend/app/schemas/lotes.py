from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from app.core.facturas import (
    MAX_FACTURA_LEN,
    MAX_FACTURAS,
    join_facturas,
    normalize_facturas_input,
    split_facturas,
)


def _normalize_pago_facturas(data: dict) -> dict:
    items = normalize_facturas_input(
        facturas=data.get("facturas"),
        numero_factura=data.get("numero_factura"),
    )
    if not items:
        raise ValueError("Debe indicar al menos una factura")
    if len(items) > MAX_FACTURAS:
        raise ValueError(f"Máximo {MAX_FACTURAS} facturas por pago")
    for item in items:
        if len(item) > MAX_FACTURA_LEN:
            raise ValueError(f"Cada factura admite máximo {MAX_FACTURA_LEN} caracteres")
    joined = join_facturas(items)
    data["facturas"] = items
    data["numero_factura"] = joined
    return data


class PagoItemCreate(BaseModel):
    proveedor_id: int
    importe: Decimal = Field(..., gt=0, decimal_places=2)
    cod_oficina: str | None = None
    fecha_limite: date | None = None
    concepto1: str = Field(..., min_length=1, max_length=80)
    concepto2: str | None = None
    concepto3: str | None = None
    concepto4: str | None = None
    facturas: list[str] | None = None
    numero_factura: str | None = Field(None, max_length=500)
    email_destino: EmailStr

    @field_validator("numero_factura", "concepto1", mode="before")
    @classmethod
    def strip_texto(cls, v):
        if v is None:
            return v
        return str(v).strip()

    @field_validator("facturas", mode="before")
    @classmethod
    def clean_facturas_list(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            return split_facturas(v)
        return v

    @model_validator(mode="after")
    def require_facturas(self):
        data = _normalize_pago_facturas(
            {"facturas": self.facturas, "numero_factura": self.numero_factura}
        )
        self.facturas = data["facturas"]
        self.numero_factura = data["numero_factura"]
        return self


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
    facturas: list[str] | None = None
    numero_factura: str | None = Field(None, max_length=500)
    email_destino: str | None = None

    @field_validator("numero_factura", "concepto1", mode="before")
    @classmethod
    def strip_texto(cls, v):
        if v is None:
            return v
        return str(v).strip()

    @field_validator("facturas", mode="before")
    @classmethod
    def clean_facturas_list(cls, v):
        if v is None:
            return v
        if isinstance(v, str):
            return split_facturas(v)
        return v

    @model_validator(mode="after")
    def normalize_if_present(self):
        if self.facturas is None and self.numero_factura is None:
            return self
        data = _normalize_pago_facturas(
            {"facturas": self.facturas, "numero_factura": self.numero_factura}
        )
        self.facturas = data["facturas"]
        self.numero_factura = data["numero_factura"]
        return self


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
    facturas: list[str] = []
    email_destino: str | None
    referencia_16: str | None
    referencia_11: str | None
    estado: str

    model_config = {"from_attributes": True}

    @model_validator(mode="after")
    def fill_facturas(self):
        if not self.facturas:
            self.facturas = split_facturas(self.numero_factura)
        return self


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
