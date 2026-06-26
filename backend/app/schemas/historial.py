from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class HistorialResumen(BaseModel):
    fecha: date
    importe_total: Decimal
    cantidad_pagos: int


class HistorialPagoItem(BaseModel):
    id: int
    lote_id: int
    lote_fecha_operacion: date
    lote_concepto: str
    lote_estado: str
    proveedor_id: int
    razon_social: str
    identificacion: str
    importe: Decimal
    numero_factura: str | None
    concepto1: str | None
    estado: str
    email_destino: str | None


class HistorialPagosResponse(BaseModel):
    resumen: HistorialResumen
    items: list[HistorialPagoItem]
    total: int
    page: int
    page_size: int
    pages: int


class HistorialPagoDetalle(BaseModel):
    id: int
    lote_id: int
    lote_fecha_operacion: date
    lote_fecha_limite: date | None
    lote_concepto: str
    lote_estado: str
    lote_importe_total: Decimal
    lote_archivo: str | None
    proveedor_id: int
    identificacion: str
    tipo_identificacion: int
    digito_verificacion: int | None
    razon_social: str
    banco_codigo: int
    banco_descripcion: str | None
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
