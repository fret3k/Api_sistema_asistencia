from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

class PersonalSchema(BaseModel):
    id: UUID
    dni: str
    nombre_completo: str
    email: str
    es_administrador: bool
    # contraseña hasheada (existe en la base de datos, no exponer en respuestas públicas)
    password_hash: str
    # Si se utiliza token de recuperación almacenado en la tabla
    password_reset_token: Optional[str] = None
    password_reset_expires_at: Optional[datetime] = None
    codificacion_facial: Optional[List[float]]

    class Config:
        from_attributes = True
