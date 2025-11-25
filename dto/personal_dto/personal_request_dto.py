from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class PersonalCreateDTO(BaseModel):
    dni: str
    nombre_completo: str
    email: EmailStr
    es_administrador: bool = False
    codificacion_facial: Optional[List[float]] = None
    # Hacer la contraseña obligatoria para respetar NOT NULL en la tabla de Supabase
    password: str = Field(..., min_length=8)
