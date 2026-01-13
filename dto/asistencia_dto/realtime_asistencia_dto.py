
"""
DTO para recibir embeddings en tiempo real desde el frontend (face-api.js)
"""
from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime

class RealtimeAsistenciaDTO(BaseModel):

    # Nuevo sistema de configuración de Pydantic v2
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "embedding": [0.01, -0.02, 0.003],
                "marca_tiempo": "2025-12-04T12:34:56.789Z",
                "tipo_registro": "ENTRADA_M",
                "imagen_base64": None
            }
        }
    )

    embedding: List[float]
    marca_tiempo: Optional[datetime] = None
    tipo_registro: Optional[str] = None
    imagen_base64: Optional[str] = None
    solo_validar: bool = False
    threshold: Optional[float] = 0.78  # Umbral de similitud configurable
    min_margin: Optional[float] = 0.08  # Margen mínimo entre matches

    @field_validator("embedding")
    def check_embedding_length(cls, v):
        if not isinstance(v, list):
            raise ValueError("embedding must be a list of floats")
        if len(v) < 64:
            raise ValueError("embedding must have at least 64 values")
        if len(v) > 512:
            raise ValueError("embedding must have at most 512 values")
        return [float(x) for x in v]
