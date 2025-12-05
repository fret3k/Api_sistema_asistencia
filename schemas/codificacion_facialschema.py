from pydantic import BaseModel
from typing import List
from uuid import UUID


class CodificacionFacialSchema(BaseModel):
    id: UUID
    personal_id: UUID
    embedding: List[float]  # vector de 128 floats

    class Config:
        from_attributes = True
