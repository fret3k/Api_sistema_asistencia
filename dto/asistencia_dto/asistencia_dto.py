from datetime import datetime
from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class RegistrarAsistenciaDTO(BaseModel):
    personal_id: UUID
    reconocimiento_valido: bool = False
    motivo: str | None = None
    tipo_registro: str | None = None
    marca_tiempo: Optional[datetime] = None