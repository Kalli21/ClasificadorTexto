from pydantic import BaseModel
from typing import List
from Models.schemas.sentences import Sentence

from Models.schemas.stats import StatsUser

class InfoGrafProducto(BaseModel):
    infoCirculo: StatsUser = StatsUser()
    comentarios: List[Sentence] = []
    comentarios_ids: List[int] = []