from pydantic import BaseModel
from typing import List, Optional
from Models.schemas.stats import StatsUser, BaseInfo, BaseStats

class InfoComentario(BaseModel):
    id: int
    contenido: str
    fecha: str
    productoId: int
    clienteId: int
    userName: str


class InfoProducto(BaseModel):
    id: int
    codProducto: str
    nombre: str
    descripcion: str
    precio: int
    urlImg: str
    usuarioId: int
    comentarios: List[InfoComentario]


class InfoCategoria(BaseModel):
    id: int
    nombre: str
    userName: str
    productos: List[InfoProducto]


class InfoProductoRanking(BaseModel):
    nombre: str = ''
    stats: StatsUser = StatsUser()

class InfoCategoriaResp(BaseModel):
    nombre: str = ''
    stats: StatsUser = StatsUser()
    
    
class InfoGrafGeneral(BaseModel):
    infoCategoria: List[InfoCategoriaResp] = []
    infoTopPos: List[InfoProductoRanking] = []
    comentariosIds: List[int] = []
    stastGeneral: StatsUser = StatsUser()
    
##############
class RequestGestionarDatos(BaseModel):
    categorias: List[InfoCategoria]
    filtrosSentimiento: List[int]
    
class InfoGrafGeneral_V2(BaseModel):
    graf_circulo: Optional[BaseStats] = None
    graf_rank_pos: Optional[List[BaseInfo]] = None
    graf_rank_neg: Optional[List[BaseInfo]] = None
    graf_bar_cat: Optional[List[BaseInfo]] = None
    graf_bar_date: Optional[List[BaseInfo]] = None