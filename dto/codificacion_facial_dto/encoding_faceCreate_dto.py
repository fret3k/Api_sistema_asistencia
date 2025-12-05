from pydantic import BaseModel
from uuid import UUID
from typing import List

class EncodingFaceCreateDTO(BaseModel):
    personal_id: UUID
    embedding: List[float]
