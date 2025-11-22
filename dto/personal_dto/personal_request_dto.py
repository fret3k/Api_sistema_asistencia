from pydantic import BaseModel, EmailStr
from typing import List, Optional

class PersonalCreateDTO(BaseModel):
    dni: str
    nombre_completo: str
    email: EmailStr
    es_administrador: bool = False
    codificacion_facial: Optional[List[float]] = None
