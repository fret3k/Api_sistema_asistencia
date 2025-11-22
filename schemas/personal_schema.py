from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class PersonalSchema(BaseModel):
    id: UUID
    dni: str
    nombre_completo: str
    email: str
    es_administrador: bool
    codificacion_facial: Optional[List[float]]

    class Config:
        from_attributes = True
