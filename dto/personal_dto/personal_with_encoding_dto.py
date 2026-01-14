from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from uuid import UUID


class PersonalWithEncodingCreateDTO(BaseModel):
    """
    DTO para registrar personal junto con su codificación facial en una sola operación.
    """
    # Datos del personal
    dni: str = Field(..., description="Documento Nacional de Identidad")
    nombre: str = Field(..., description="Nombre del personal")
    apellido_paterno: str = Field(..., description="Apellido paterno")
    apellido_materno: str = Field(..., description="Apellido materno")
    email: EmailStr = Field(..., description="Correo electrónico del personal")
    es_administrador: bool = Field(default=False, description="Indica si el personal es administrador")
    password: str = Field(..., min_length=8, description="Contraseña del personal (mínimo 8 caracteres)")
    
    # Datos de la codificación facial
    embedding: List[float] = Field(..., description="Vector de embedding facial (array de 128 números flotantes)")
    
    # Foto de perfil
    foto_base64: Optional[str] = Field(None, description="Imagen de perfil en formato string base64Data")


class PersonalWithEncodingResponseDTO(BaseModel):
    """
    DTO de respuesta para el registro combinado de personal y encoding facial.
    """
    personal_id: UUID = Field(..., description="ID del personal creado")
    encoding_id: UUID = Field(..., description="ID de la codificación facial creada")
    message: str = Field(..., description="Mensaje de confirmación")

