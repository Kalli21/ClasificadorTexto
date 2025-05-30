from pydantic import BaseModel

class BaseStats(BaseModel):
    total: int = 0
    pos: int = 0
    net: int = 0
    neg: int = 0

class StatsUser(BaseStats):
    # 0 -> No Analizado ,  1 -> Analisando 2 -> Analisis terminado 
    estado: int = 0
    
class BaseInfo(BaseStats):
    correlativo: int = 0
    nombre: str = ''