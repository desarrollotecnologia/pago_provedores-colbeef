from pydantic import BaseModel


class CatalogoItem(BaseModel):
    codigo: int
    descripcion: str

    model_config = {"from_attributes": True}


class BancoCatalogo(BaseModel):
    codigo: int
    descripcion: str

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    message: str
