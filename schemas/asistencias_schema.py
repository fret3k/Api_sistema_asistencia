from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class AsistenciaSchema(BaseModel):
    id: UUID
    personal_id: UUID
    fecha: datetime
    marca_tiempo: datetime
    tipo_registro: str
    estado: str
    motivo: str | None = None

    class Config:
        from_attributes = True
