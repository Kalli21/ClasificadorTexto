from fastapi import FastAPI, HTTPException
from typing import List, Optional
from Models.schemas.infoGrafGeneral import  InfoGrafGeneral_V2, RequestGestionarDatos
from Models.schemas.request.filtroComentario import FiltroComentario, FiltroSentences
from Models.schemas.sentences import Sentence
from Models.schemas.stats import StatsUser, BaseStats, BaseInfo
from Models_IA.service import IAservices
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware

from Repository.main import FireRepository

app = FastAPI()

# Configuración de CORS
origins = [
    "http://localhost",
    "http://localhost:4200",
    "http://127.0.0.1:8888",
    "http://54.87.222.35",
    "http://54.83.42.195:8080",
    "http://proyecto-tesis-acfront-angular.s3-website-us-east-1.amazonaws.com"    
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resto del código de tu aplicación FAST API


repo = FireRepository()
# Se carga el modelo al inicio, en este caso siempre se va a usar el mismo modelo.
model =  IAservices()

@app.post("/subir/{user_id}")
def set_comentarios(user_id,comentarios:List[Sentence], persit_stats: Optional[bool] = False):
    repo.set_prediciones(user_id,comentarios)
    stats = StatsUser()
    if persit_stats:
        repo_stat = repo.get_stats(user_id)
        if repo_stat:
            stats = StatsUser(**repo_stat)
            stats.estado = 0
    repo.set_stats(user_id,stats)
    return HTTPException(status_code=200, detail="Comentarios subidos")

@app.get("/predecir/{user_id}")
def text_clasificador(user_id, predic_all: Optional[bool] = False):
    if repo.user_exist(user_id):
        # model =  IAservices()
        print("predic_all", predic_all)
        filtro = None
        ini_stats = repo.get_stats(user_id)
        aux_stats = None
        if not predic_all:
            filtro = FiltroSentences()
            filtro.categoriasId.append(-1)
            aux_stats = ini_stats
        comentarios = repo.get_predicciones(user_id, filtro)
        if len(comentarios)==0:
            return {'msg': "No hay comentarios a procesar"}    
        resultados, user_stats = model.text_clasificacion(comentarios, aux_stats)
        # json_resultados = jsonable_encoder(resultados)
        repo.update_predicciones(user_id,resultados)
        
        repo.update_base_stats(user_id,user_stats)        
        json_resultados = jsonable_encoder(user_stats)
        return json_resultados
    return HTTPException(status_code=404, detail="Usuario no encontrado")


@app.get("/stats/{user_id}")
def get_stats(user_id):
    return repo.get_stats(user_id)
    
@app.post("/stats/{user_id}")
def build_stats(user_id, ids:List[str],filtro:List[int]):
    return repo.build_stats(user_id,ids,filtro)

@app.put("/stats/{user_id}")
def text_clasificador(user_id, stast: StatsUser):
    return repo.update_stats(user_id, stast)    
    
# Obtener todas las oraciones
@app.post("/comentarios/{user_id}", response_model=List[Sentence])
def get_sentences(user_id: str, filtros:Optional[FiltroSentences]):
    sentences = repo.get_predicciones(user_id, filtros)
    return sentences

# Obtener una oración por su ID
@app.get("/comentarios/{user_id}/{sentence_id}", response_model=Sentence)
def get_sentence(user_id: str,sentence_id: str):
    sentence = repo.get_prediccion(user_id,sentence_id)
    if not sentence:
        raise HTTPException(status_code=404, detail="Comentarios no encontrado")
    return sentence

# Actualizar oraciones existentes
@app.put("/comentarios/{user_id}")
def update_sentences(user_id: str ,sentences: List[Sentence]):
    updated_sentences = repo.update_predicciones(user_id,sentences)
    if not updated_sentences:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")
    return updated_sentences

# Eliminar oraciones
@app.delete("/delete/{user_id}/{sentence_id}")
def delete_sentences(user_id: str, sentence_id: str):
    deleted = repo.deled_prediccion(user_id, sentence_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")

# Eliminar informacion User
@app.delete("/delete/{user_id}")
def delete_user(user_id: str):
    deleted = repo.delete_user(user_id)
    return deleted
##################
#########
@app.post("/comentarios/group/{user_id}")
def get_comentarios_group_fecha(user_id: str,filtros:FiltroComentario):
    resultados = repo.get_comentarios_group_fecha(user_id,filtros)
    json_resultados = jsonable_encoder(resultados)
    return json_resultados
    

@app.post("/getionar/{user_id}")
def gestionar_info(user_id: str,req: RequestGestionarDatos):
    resultados = repo.gestionar_info(user_id,req)      
    json_resultados = jsonable_encoder(resultados)
    return json_resultados


###########
@app.post("/info/general/{user_id}")
async def create_info_general(user_id: str, info: InfoGrafGeneral_V2):
    coll = "info_general"    
    resultados = await repo.clear_and_set_info(user_id ,coll, info)
    json_resultados = jsonable_encoder(resultados)
    return json_resultados

@app.post("/info/producto/{user_id}")
async def create_info_producto(user_id: str, info: InfoGrafGeneral_V2):
    coll = "info_producto"
    info.graf_rank_pos = None
    info.graf_rank_neg = None
    resultados = await repo.clear_and_set_info(user_id ,coll, info)
    json_resultados = jsonable_encoder(resultados)
    return json_resultados
