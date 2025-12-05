from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class PersonalUpdateDTO(BaseModel):
    """
    DTO para actualización parcial de personal.
    Todos los campos son opcionales.
    """

    nombre: Optional[str] = None
    apellido_paterno: Optional[str] = None
    apellido_materno: Optional[str] = None
    email: Optional[EmailStr] = None
    es_administrador: Optional[bool] = None
    password: Optional[str] = Field(default=None, min_length=8)
