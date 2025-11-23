from pydantic import BaseModel
from uuid import UUID

class RegistrarAsistenciaDTO(BaseModel):
    personal_id: UUID
    reconocimiento_valido: bool
    motivo: str | None = None