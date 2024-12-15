from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Sentence(BaseModel):
    id: str = ''
    text: str
    probabilidades: List[float] = [] 
    categoria: int = -1
    fecha: Optional[datetime]