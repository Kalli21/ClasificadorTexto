
from Models.schemas.sentences import Sentence
import numpy as np
from Models_IA.textClasificacion import clasificacion_text
from typing import List

class IAservices():
    
    def text_clasificacion(self,comentarios,ids):
        model =  clasificacion_text()
        result_np = model.predecir_text(comentarios)  # Convertir en una lista de Python
        result_np = np.array(result_np)  # Convertir a un arreglo NumPy
        result_list = result_np.tolist()
        
        result = []
        i=0
        for c in comentarios:
            coment = Sentence(text = c)
            coment.id = ids[i]
            coment.probabilidades = result_list[i]            
            coment.categoria = int(np.argmax(result_list[i]))
            i+=1
            result.append(coment)
        return result
            
            