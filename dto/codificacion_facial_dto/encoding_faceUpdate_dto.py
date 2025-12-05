from typing import List

from pydantic import BaseModel


class EncodingFaceUpdateDTO(BaseModel):
    embedding: List[float]
