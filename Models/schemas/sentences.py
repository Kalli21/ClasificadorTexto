from pydantic import BaseModel
from typing import List

class Sentence(BaseModel):
    id: str = ''
    text: str
    probabilidades: List[float] = [] 
    categoria: int = -1