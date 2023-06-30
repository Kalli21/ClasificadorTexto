from pydantic import BaseModel
from typing import List
from datetime import datetime

class Sentence(BaseModel):
    id: str = ''
    text: str
    probabilidades: List[float] = [] 
    categoria: int = -1
    fecha: datetime