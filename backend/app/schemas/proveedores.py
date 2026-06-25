from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class ProveedorBase(BaseModel):
    identificacion: str = Field(..., min_length=1, max_length=20)
    tipo_identificacion: int = Field(..., ge=1, le=9)
    digito_verificacion: int | None = Field(None, ge=0, le=9)
    razon_social: str = Field(..., min_length=1, max_length=200)
    forma_pago: int = Field(1, ge=1)
    banco_codigo: int = Field(..., ge=1)
    tipo_cuenta: int = Field(..., ge=1, le=2)
    numero_cuenta: str = Field(..., min_length=1, max_length=20)
    cod_oficina: str | None = Field(None, max_length=10)
    email: str | None = None

    @field_validator("cod_oficina", mode="before")
    @classmethod
    def normalize_cod_oficina(cls, v):
        if v is None or str(v).strip() == "":
            return None
        return str(v).strip()

    @field_validator("identificacion", "numero_cuenta", "razon_social", mode="before")
    @classmethod
    def strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("razon_social")
    @classmethod
    def uppercase_name(cls, v: str) -> str:
        return v.upper()

    @field_validator("email")
    @classmethod
    def normalize_email_create(cls, v: str | None) -> str | None:
        if v is None or str(v).strip() == "":
            return None
        return str(v).strip().lower()


class ProveedorCreate(ProveedorBase):
    pass


class ProveedorUpdate(BaseModel):
    identificacion: str | None = Field(None, min_length=1, max_length=20)
    tipo_identificacion: int | None = Field(None, ge=1, le=9)
    digito_verificacion: int | None = Field(None, ge=0, le=9)
    razon_social: str | None = Field(None, min_length=1, max_length=200)
    forma_pago: int | None = Field(None, ge=1)
    banco_codigo: int | None = Field(None, ge=1)
    tipo_cuenta: int | None = Field(None, ge=1, le=2)
    numero_cuenta: str | None = Field(None, min_length=1, max_length=20)
    cod_oficina: str | None = Field(None, max_length=10)
    email: str | None = None
    activo: bool | None = None

    @field_validator("identificacion", "numero_cuenta", "razon_social", "cod_oficina", mode="before")
    @classmethod
    def strip_strings_update(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("cod_oficina", mode="before")
    @classmethod
    def normalize_cod_oficina_update(cls, v):
        if v is None or str(v).strip() == "":
            return None
        return str(v).strip()

    @field_validator("razon_social")
    @classmethod
    def uppercase_name(cls, v: str | None) -> str | None:
        return v.upper() if v else v

    @field_validator("email")
    @classmethod
    def normalize_email(cls, v: str | None) -> str | None:
        if v is None or str(v).strip() == "":
            return None
        return str(v).strip().lower()


class BancoInfo(BaseModel):
    codigo: int
    descripcion: str

    model_config = {"from_attributes": True}


class ProveedorResponse(BaseModel):
    id: int
    identificacion: str
    tipo_identificacion: int
    digito_verificacion: int | None
    razon_social: str
    forma_pago: int
    banco_codigo: int
    tipo_cuenta: int
    numero_cuenta: str
    cod_oficina: str | None
    email: str | None
    activo: bool
    creado_en: datetime
    actualizado_en: datetime
    banco: BancoInfo | None = None

    model_config = {"from_attributes": True}


class ProveedorListResponse(BaseModel):
    items: list[ProveedorResponse]
    total: int
    page: int
    page_size: int
    pages: int
