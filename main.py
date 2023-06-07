from fastapi import FastAPI, HTTPException
from typing import List
from Models.schemas.sentences import Sentence
from Models.schemas.stats import StatsUser
from Models_IA.service import IAservices
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware

from Repository.main import FireRepository

app = FastAPI()

# Configuración de CORS
origins = [
    "http://localhost",
    "http://localhost:4200",  # Agrega la URL de tu aplicación Angular aquí
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
def set_comentarios(user_id,comentarios:List[Sentence]):
    repo.set_prediciones(user_id,comentarios)
    stats = StatsUser()
    repo.set_stats(user_id,stats)
    return HTTPException(status_code=200, detail="Comentarios subidos")

@app.get("/predecir/{user_id}")
def text_clasificador(user_id):
    if repo.user_exist(user_id):
        # model =  IAservices()
        comentarios = repo.get_predicciones(user_id)    
        resultados, user_stats = model.text_clasificacion(comentarios)
        json_resultados = jsonable_encoder(resultados)
        repo.update_predicciones(user_id,resultados)
        repo.update_stats(user_id,user_stats)
        return json_resultados
    return HTTPException(status_code=404, detail="Usuario no encontrado")


@app.get("/stats/{user_id}")
def text_clasificador(user_id):
    return repo.get_stats(user_id)
    

# Obtener todas las oraciones
@app.get("/comentarios/{user_id}", response_model=List[Sentence])
def get_sentences(user_id: str):
    sentences = repo.get_predicciones(user_id)
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