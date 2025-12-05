from pydantic import BaseModel, EmailStr, Field

class CodingFaceCreateRequest(BaseModel):
    dni: str
    nombre: str
    apellido_paterno: str
    apellido_materno: str
    email: EmailStr
    es_administrador: bool = False
    password: str = Field(..., min_length=8)
