from pydantic import BaseModel, ConfigDict
from datetime import time
from typing import Optional


class HorarioItemDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    a_tiempo: Optional[time] = None
    tarde: Optional[time] = None
    limite_temprano: Optional[time] = None


class HorariosUpdateDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ENTRADA_M: Optional[HorarioItemDTO] = None
    SALIDA_M: Optional[HorarioItemDTO] = None
    ENTRADA_T: Optional[HorarioItemDTO] = None
    SALIDA_T: Optional[HorarioItemDTO] = None
