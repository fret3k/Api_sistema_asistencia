from pydantic import BaseModel
from uuid import UUID
from datetime import date, datetime

class SolicitudSobretiempoSchema(BaseModel):
    id: UUID
    personal_id: UUID
    fecha_trabajo: date
    horas_solicitadas: float
    razon: str
    estado_solicitud: str
    fecha_solicitud: datetime

    class Config:
        from_attributes = True

