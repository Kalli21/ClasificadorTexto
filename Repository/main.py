import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from typing import List
from Models.schemas.infoGrafGeneral import  InfoCategoria, InfoCategoriaResp, InfoGrafGeneral_V2, InfoGrafGeneral, InfoProductoRanking, RequestGestionarDatos
from Models.schemas.infoGrafProducto import InfoGrafProducto
from Models.schemas.request.filtroComentario import FiltroComentario, FiltroSentences

from Models.schemas.sentences import Sentence
from Models.schemas.stats import StatsUser, BaseStats
from math import ceil
from fastapi.encoders import jsonable_encoder

from google.cloud.firestore import FieldFilter

class FireRepository():
    
    cred = credentials.Certificate("credenciales/clasificadortexto-firebase-adminsdk-hwvq5-21bd3f8190.json")
    firebase_admin.initialize_app(cred)

    db = firestore.client()

    
    def get_stats(self,user_id):
        return self.db.collection('usuarios').document(user_id).get().to_dict() 
        
    def set_stats(self,user_id,stats:StatsUser):
        return self.db.collection('usuarios').document(user_id).set(stats.dict())
                
    def update_stats(self,user_id,stats:StatsUser):
        # Convierte el objeto StatsUser a un diccionario serializable
        stats_dict = jsonable_encoder(stats)        
        # Actualiza el documento en Firestore
        self.db.collection('usuarios').document(user_id).update(stats_dict)
     
    def update_base_stats(self,user_id,stats:BaseStats):
        # Convierte el objeto StatsUser a un diccionario serializable
        stats_dict = jsonable_encoder(stats)        
        # Actualiza el documento en Firestore
        self.db.collection('usuarios').document(user_id).update(stats_dict) 
        
    def build_stats(self,user_id,ids,filtro):
        stats = StatsUser()
        listSentences = []
        listIds= []
        aux = [0,0,0]
        for i in ids:
            coment:Sentence = self.get_prediccion(user_id,i)
            if coment:
                if( coment['categoria'] in filtro):
                    listSentences.append(coment)  
                    listIds.append(coment['id'])              
                    aux[coment['categoria']] += 1
        stats.neg = aux[0]
        stats.net = aux[1]
        stats.pos = aux[2]
        stats.total = sum(aux)
        return InfoGrafProducto(infoCirculo=stats,comentarios=listSentences,comentarios_ids=listIds)
    
    def set_prediciones(self,user_id,comentarios: List[Sentence]):
        batch = self.db.batch()
        sentences_collection = self.db.collection('usuarios').document(user_id).collection('comentarios')  # Se obtiene una referencia de documento para la colección

        for comentario in comentarios:
            doc_ref = sentences_collection.document(comentario.id)  # Obtener una referencia de documento única para cada objeto Sentence
            batch.set(doc_ref, comentario.dict())

        batch.commit()
        return sentences_collection.id

    def get_predicciones(self, user_id, filtro: FiltroSentences  = None):
        sentences = []
        docs = self.db.collection('usuarios').document(user_id).collection('comentarios')
        
        if filtro:
            if len(filtro.listId)>0: docs = docs.where(filter = FieldFilter('id', 'in', filtro.listId))
            if filtro.fechaIni: docs = docs.where(filter = FieldFilter('fecha', '>=', filtro.fechaIni))
            if filtro.fechaFin: docs = docs.where(filter = FieldFilter('fecha', '<=', filtro.fechaFin))
            if len(filtro.categoriasId)>0: docs = docs.where(filter = FieldFilter('categoria', 'in', filtro.categoriasId))
        
        docs = docs.get()
    
        for doc in docs:
            sentence_data = doc.to_dict()  # Obtener los datos del documento como un diccionario
            sentence = Sentence(**sentence_data)  # Crear una instancia de Sentence usando los datos del documento            
            sentences.append(sentence)                
                
        return sentences

    def get_prediccion(self,user_id,coment_id):
        collection_ref = self.db.collection('usuarios').document(user_id).collection('comentarios')
        return collection_ref.document(coment_id).get().to_dict() 

    def update_predicciones(self,user_id: str, comentarios: List[Sentence]):
        # batch = self.db.batch()

        # for sentence in comentarios:
        #     # Excluir el campo 'id' del diccionario de datos
        #     sentence_data = sentence.dict(exclude={'id'})
        #     doc_ref = self.db.collection('usuarios').document(user_id).collection('comentarios').document(sentence.id)
        #     batch.update(doc_ref, sentence_data)

        # batch.commit()
        # return comentarios
        MAX_BATCH_SIZE = 500  # Tamaño máximo del lote

        # Dividir los comentarios en lotes más pequeños
        num_batches = ceil(len(comentarios) / MAX_BATCH_SIZE)
        batches = [comentarios[i:i+MAX_BATCH_SIZE] for i in range(0, len(comentarios), MAX_BATCH_SIZE)]

        for batch in batches:
            batch_update = self.db.batch()

            for sentence in batch:
                sentence_data = sentence.dict(exclude={'id'})
                doc_ref = self.db.collection('usuarios').document(user_id).collection('comentarios').document(sentence.id)
                batch_update.update(doc_ref, sentence_data)

            batch_update.commit()

        return comentarios

    def deled_prediccion(self,user_id,coment_id):
        comment_ref = self.db.collection('usuarios').document(user_id).collection('comentarios').document(coment_id)
        comment_doc = comment_ref.get()

        if comment_doc.exists:
            comment_ref.delete()
            return True
        else:
            return False

    def user_exist(self,user_id):
        comment_ref = self.db.collection('usuarios').document(user_id)
        comment_doc = comment_ref.get()

        if comment_doc.exists:
            return True
        else:
            return False

    def delete_user(self, user_id):
        # Obtén una referencia al documento principal
        user_ref = self.db.collection('usuarios').document(user_id)

        # Verifica si el documento existe
        if user_ref.get().exists:
            # Elimina las subcolecciones usando lotes
            self._delete_subcollections_in_batches(user_ref)

            # Elimina el documento principal
            user_ref.delete()
            return True
        else:
            return False

    def _delete_subcollections_in_batches(self, document_ref):
        # Obtén todas las subcolecciones
        subcollections = document_ref.collections()

        for subcollection in subcollections:
            while True:
                # Obtén hasta 500 documentos de la subcolección
                docs = list(subcollection.limit(500).stream())

                if not docs:
                    break  # Si no hay más documentos, termina el ciclo

                # Inicia un batch
                batch = self.db.batch()

                # Añade cada documento al batch para eliminar
                for doc in docs:
                    batch.delete(doc.reference)

                # Ejecuta el batch
                batch.commit()
###########
    def gestionar_info(self,user_id: str,req: RequestGestionarDatos):
        resp = []
        prodRank = []
        coment_ids = []
        stastGeneral = StatsUser()
        obj = req.categorias
        for cat in obj:
            newCat = InfoCategoriaResp()
            newCat.nombre = cat.nombre
            
            for prod in cat.productos:
                newPrd = InfoProductoRanking()
                newPrd.nombre = prod.nombre
                ids = []
                for com in prod.comentarios:
                    ids.append(str(com.id))
                    # coment_ids.append(str(com.id))
                statsBuildAux = self.build_stats(user_id,ids,req.filtrosSentimiento)
                coment_ids.extend(statsBuildAux.comentarios_ids)
                newPrd.stats = statsBuildAux.infoCirculo
                newCat.stats.neg += newPrd.stats.neg
                newCat.stats.net += newPrd.stats.net
                newCat.stats.pos += newPrd.stats.pos
                newCat.stats.total += newPrd.stats.total
                prodRank.append(newPrd)
            stastGeneral.neg += newCat.stats.neg
            stastGeneral.net += newCat.stats.net
            stastGeneral.pos += newCat.stats.pos
            stastGeneral.total += newCat.stats.total
            resp.append(newCat)
        prodRank = sorted(prodRank, key=lambda x: x.stats.pos, reverse=True)
        result = InfoGrafGeneral()
        result.infoCategoria = resp
        result.infoTopPos = prodRank
        result.comentariosIds = coment_ids
        result.stastGeneral = stastGeneral
        return result
        
    def get_comentarios_group_fecha(self,user_id,filtros:FiltroComentario):
        # Obtener una referencia a la colección de comentarios
        sentences_collection = self.db.collection('usuarios').document(user_id).collection('comentarios')

        # Crear un diccionario para agrupar los comentarios por mes y año
        comentarios_agrupados = {}     
        
        
        # Realizar la consulta y obtener los comentarios ordenados por fecha
        if( not filtros.filtrarIds ):            
            query = sentences_collection.order_by('fecha').get()
            self.iterarQuery(query,comentarios_agrupados)
        else :
            if( not filtros or not filtros.comentarios_id or len(filtros.comentarios_id) == 0 ):
                return comentarios_agrupados
            # query = sentences_collection.where('id', 'in', filtros.comentarios_id).get()
            # Dividir la lista de IDs en subconjuntos más pequeños
            subconjuntos_ids = [filtros.comentarios_id[i:i + 30] for i in range(0, len(filtros.comentarios_id), 30)]

            # Realizar consultas separadas para cada subconjunto de IDs
            for subconjunto in subconjuntos_ids:
                query = sentences_collection.where('id', 'in', subconjunto).get()
                self.iterarQuery(query,comentarios_agrupados)
            
        # Calcular el número de veces que se repite cada categoría (0, 1, 2) en cada mes
        for anio, meses in comentarios_agrupados.items():
            for mes, comentarios in meses.items():
                categorias_count = [0, 0, 0]
                for comentario in comentarios:
                    categoria = comentario.get('categoria')
                    categorias_count[categoria] += 1
                comentarios_agrupados[anio][mes].append((('cantCategoria', categorias_count),('anio', anio),('mes', mes)))


        return comentarios_agrupados
    
    def iterarQuery(self,query,comentarios_agrupados):
        # Recorrer los documentos y agruparlos por mes y año
        for doc in query:
            fecha = doc.get('fecha')  # Obtener el objeto Timestamp directamente
            
            # Obtener el año y mes de la fecha
            anio = fecha.year
            mes = fecha.month
            
            # Agrupar los comentarios por mes y año
            if anio not in comentarios_agrupados:
                comentarios_agrupados[anio] = {}
            
            if mes not in comentarios_agrupados[anio]:
                comentarios_agrupados[anio][mes] = []
            
            comentarios_agrupados[anio][mes].append(doc.to_dict())
            
###### SET INFOR

    async def clear_and_set_info(self, user_id: str, coll : str, list_info: InfoGrafGeneral_V2):
        # Obtiene la referencia de la subcolección
        subcollection_ref = self.db.collection('usuarios').document(user_id).collection(coll)

        # 1. Elimina todos los documentos en la subcolección
        await self._clear_subcollection(subcollection_ref)
        
        body = list_info.dict()
        subcollection_ref.add(body)
        
        # 2. Inserta los nuevos elementos en la subcolección
        # for item in list_info:
        #     body = item.dict()  
        #     subcollection_ref.add(body)

        return f"Se inserto informacion de {coll}"

    async def _clear_subcollection(self, subcollection_ref):
        # Obtiene todos los documentos de la subcolección
        docs = subcollection_ref.stream()
        # Elimina cada documento encontrado
        for doc in docs:
            doc.reference.delete()
            

