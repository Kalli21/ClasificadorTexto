from pydantic import BaseModel
from typing import List, Optional
from Models.schemas.stats import StatsUser
from datetime import datetime

class FiltroComentario(BaseModel):
    comentarios_id: List[str] = []
    filtrarIds: bool = False

class FiltroSentences(BaseModel):
    fechaIni: Optional[datetime] = None
    fechaFin: Optional[datetime] = None
    categoriasId: List[int] = []
    listId: List[str] = []  