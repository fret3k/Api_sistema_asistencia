from pydantic import BaseModel
from uuid import UUID

class RegistrarAsistenciaDTO(BaseModel):
    personal_id: UUID
    reconocimiento_valido: bool = False
    motivo: str | None = None
    tipo_registro: str | None = None