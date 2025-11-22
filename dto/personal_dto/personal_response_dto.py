from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class PersonalResponseDTO(BaseModel):
    id: UUID
    dni: str
    nombre_completo: str
    email: str
    es_administrador: bool
    codificacion_facial: Optional[List[float]]
