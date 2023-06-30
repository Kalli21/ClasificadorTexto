from pydantic import BaseModel
from typing import List
from Models.schemas.stats import StatsUser

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
    
