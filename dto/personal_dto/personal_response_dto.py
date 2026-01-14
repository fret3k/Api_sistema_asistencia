from uuid import UUID
from datetime import datetime

from pydantic import EmailStr, BaseModel


class PersonalResponseDTO(BaseModel):
    id: UUID
    dni: str
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    email: EmailStr
    es_administrador: bool
    foto_base64: str | None = None

    class Config:
        from_attributes = True

