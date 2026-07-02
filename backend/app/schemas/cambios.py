from datetime import date, datetime

from pydantic import BaseModel


class CambiosResumen(BaseModel):
    fecha_desde: date
    fecha_hasta: date
    cantidad_cambios: int
    creaciones: int
    ediciones: int
    desactivaciones: int


class CambioProveedorItem(BaseModel):
    id: int
    registrado_en: datetime
    accion: str
    proveedor_id: int
    razon_social: str
    identificacion: str
    usuario_id: int
    usuario_nombre: str
    resumen: str
    cantidad_cambios: int


class CambioCampo(BaseModel):
    campo: str
    etiqueta: str
    anterior: str | None
    nuevo: str | None


class CambioProveedorDetalle(CambioProveedorItem):
    cambios: list[CambioCampo]
    snapshot: dict | None = None


class CambiosProveedorResponse(BaseModel):
    resumen: CambiosResumen
    items: list[CambioProveedorItem]
    total: int
    page: int
    page_size: int
    pages: int
