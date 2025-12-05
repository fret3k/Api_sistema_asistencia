from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class PersonalSchema(BaseModel):
    id: UUID
    dni: str
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    email: str
    es_administrador: bool

    # información sensible interna
    password_hash: str
    password_reset_token: Optional[str] = None
    password_reset_expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True

