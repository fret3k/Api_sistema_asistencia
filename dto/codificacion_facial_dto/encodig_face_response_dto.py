
from pydantic import BaseModel
from uuid import UUID
from typing import List
from datetime import datetime

class EncodingFaceResponseDTO(BaseModel):
    id: UUID
    personal_id: UUID
    embedding: List[float]  # vector de 128 floats

    class Config:
        from_attributes = True
