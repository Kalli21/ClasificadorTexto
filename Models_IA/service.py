
from Models.schemas.sentences import Sentence
import numpy as np
from Models.schemas.stats import StatsUser
from Models_IA.textClasificacion import clasificacion_text
from typing import List

class IAservices():
    
    def text_clasificacion(self,comentarios):
        model =  clasificacion_text()
        com_text = self._trans_comentarios(comentarios) 
        result_np = model.predecir_text(com_text)  # Convertir en una lista de Python
        result_np = np.array(result_np)  # Convertir a un arreglo NumPy
        result_list = result_np.tolist()
        
        stats = StatsUser()
        lis_aux = [0,0,0]
        i=0
        for c in comentarios:
            c.probabilidades = result_list[i]            
            c.categoria = int(np.argmax(result_list[i]))
            lis_aux[c.categoria] += 1
            i+=1
        stats.total = i
        stats.neg = lis_aux[0]
        stats.net = lis_aux[1]       
        stats.pos = lis_aux[2]
        return comentarios, stats
    
    def _trans_comentarios(self,comentarios):
        list_text = []
        for c in comentarios:
            list_text.append(c.text)
        return list_text