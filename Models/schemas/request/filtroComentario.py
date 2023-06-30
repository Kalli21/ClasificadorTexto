from pydantic import BaseModel
from typing import List
from Models.schemas.stats import StatsUser

class FiltroComentario(BaseModel):
    comentarios_id: List[str] = []
    filtrarIds: bool = False
