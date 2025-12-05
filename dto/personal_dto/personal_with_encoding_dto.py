from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List
from uuid import UUID


class PersonalWithEncodingCreateDTO(BaseModel):
    """
    DTO para registrar personal junto con su codificación facial en una sola operación.
    """
    # Datos del personal
    dni: str = Field(..., description="Documento Nacional de Identidad", min_length=1, max_length=20)
    nombre: str = Field(..., description="Nombre del personal", min_length=1, max_length=100)
    apellido_paterno: str = Field(..., description="Apellido paterno", min_length=1, max_length=100)
    apellido_materno: str = Field(..., description="Apellido materno", min_length=1, max_length=100)
    email: EmailStr = Field(..., description="Correo electrónico del personal")
    es_administrador: bool = Field(default=False, description="Indica si el personal es administrador")
    password: str = Field(..., min_length=8, description="Contraseña del personal (mínimo 8 caracteres)")
    
    # Datos de la codificación facial
    embedding: List[float] = Field(
        ..., 
        description="Vector de embedding facial (array de 128 números flotantes)",
        min_length=128,
        max_length=128
    )
    
    @field_validator('embedding')
    @classmethod
    def validate_embedding(cls, v):
        """Valida que el embedding tenga exactamente 128 valores numéricos."""
        if not isinstance(v, list):
            raise ValueError("El embedding debe ser un array")
        if len(v) != 128:
            raise ValueError(f"El embedding debe tener exactamente 128 valores, se recibieron {len(v)}")
        if not all(isinstance(x, (int, float)) for x in v):
            raise ValueError("Todos los valores del embedding deben ser números")
        return [float(x) for x in v]  # Asegurar que todos sean floats


class PersonalWithEncodingResponseDTO(BaseModel):
    """
    DTO de respuesta para el registro combinado de personal y encoding facial.
    """
    personal_id: str = Field(..., description="ID del personal creado (UUID como string)")
    encoding_id: str = Field(..., description="ID de la codificación facial creada (UUID como string)")
    message: str = Field(..., description="Mensaje de confirmación")

