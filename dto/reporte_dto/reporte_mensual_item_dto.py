from pydantic import BaseModel
from uuid import UUID

class ReporteMensualItemDTO(BaseModel):
    numero: int
    dni: str
    apellidos_y_nombres: str
    dias_laborables: int
    dias_asistidos: int
    tardanzas: int
    faltas: int
    ausencias_justificadas: int
    salidas_anticipadas: int
    horas_sobretiempo: float
    horas_trabajadas: float
    total_horas: float
    observaciones: str
