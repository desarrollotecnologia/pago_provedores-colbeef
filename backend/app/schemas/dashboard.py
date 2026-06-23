from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class DashboardResumen(BaseModel):
    fecha_desde: date
    fecha_hasta: date
    importe_total: Decimal
    cantidad_proveedores: int
    cantidad_lotes: int
    cantidad_pagos: int


class TopProveedor(BaseModel):
    proveedor_id: int
    razon_social: str
    total_pagado: Decimal
    cantidad_pagos: int


class DashboardResponse(BaseModel):
    resumen: DashboardResumen
    top_proveedores: list[TopProveedor]
    ultimos_lotes: list[dict]


class PublicConfig(BaseModel):
    app_name: str
    app_url: str
    api_base: str
    version: str
    env: str
