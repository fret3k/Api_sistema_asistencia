from pydantic import BaseModel
from uuid import UUID
from datetime import date, time, datetime
from typing import Optional

class SolicitudAusenciaSchema(BaseModel):
    id: UUID
    personal_id: UUID
    tipo_ausencia: str
    fecha_inicio: date
    fecha_fin: date
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    razon: str
    estado_solicitud: str
    fecha_solicitud: datetime

    class Config:
        from_attributes = True

