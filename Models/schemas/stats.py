from pydantic import BaseModel

class StatsUser(BaseModel):
    total: int = 0
    pos: int = 0
    net: int = 0
    neg: int = 0