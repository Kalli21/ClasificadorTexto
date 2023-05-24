from fastapi import FastAPI, HTTPException
from typing import List
from Models.schemas.sentences import Sentence
from Models_IA.service import IAservices
from fastapi.encoders import jsonable_encoder

from Repository.main import *

app = FastAPI()

@app.post("/predecir")
def text_clasificador(user_id,comentarios: List[str],ids: List[str]):
    model =  IAservices()    
    resultados = model.text_clasificacion(comentarios,ids)
    json_resultados = jsonable_encoder(resultados)
    set_prediciones(user_id,resultados)
    return json_resultados

# Obtener todas las oraciones
@app.get("/comentarios/{user_id}", response_model=List[Sentence])
def get_sentences(user_id: str):
    sentences = get_predicciones(user_id)
    return sentences

# Obtener una oración por su ID
@app.get("/comentarios/{user_id}/{sentence_id}", response_model=Sentence)
def get_sentence(user_id: str,sentence_id: str):
    sentence = get_prediccion(user_id,sentence_id)
    if not sentence:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")
    return sentence

# Actualizar oraciones existentes
@app.put("/comentarios")
def update_sentences(user_id: str ,sentences: List[Sentence]):
    updated_sentences = update_predicciones(user_id,sentences)
    if not updated_sentences:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")
    return updated_sentences

# Eliminar oraciones
@app.delete("/delete")
def delete_sentences(user_id: str, sentence_id: str):
    deleted = deled_prediccion(user_id, sentence_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Comentario no encontrado")