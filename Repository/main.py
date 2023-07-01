import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from typing import List
from Models.schemas.infoGrafProducto import InfoGrafProducto
from Models.schemas.request.filtroComentario import FiltroComentario

from Models.schemas.sentences import Sentence
from Models.schemas.stats import StatsUser

class FireRepository():
    
    cred = credentials.Certificate("credenciales/clasificadortexto-firebase-adminsdk-hwvq5-21bd3f8190.json")
    firebase_admin.initialize_app(cred)

    db = firestore.client()

    
    def get_stats(self,user_id):
        return self.db.collection('usuarios').document(user_id).get().to_dict() 
        
    def set_stats(self,user_id,stats:StatsUser):
        return self.db.collection('usuarios').document(user_id).set(stats.dict())
        
        
    def update_stats(self,user_id,stats:StatsUser):
        return self.db.collection('usuarios').document(user_id).update(stats.dict())
        
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

    def get_predicciones(self,user_id):
        sentences = []
        collection_ref = self.db.collection('usuarios').document(user_id).collection('comentarios').get()

        for doc in collection_ref:
            sentence_data = doc.to_dict()  # Obtener los datos del documento como un diccionario
            sentence = Sentence(**sentence_data)  # Crear una instancia de Sentence usando los datos del documento
            sentences.append(sentence)

        return sentences

    def get_prediccion(self,user_id,coment_id):
        collection_ref = self.db.collection('usuarios').document(user_id).collection('comentarios')
        return collection_ref.document(coment_id).get().to_dict() 

    def update_predicciones(self,user_id: str, comentarios: List[Sentence]):
        batch = self.db.batch()

        for sentence in comentarios:
            # Excluir el campo 'id' del diccionario de datos
            sentence_data = sentence.dict(exclude={'id'})
            doc_ref = self.db.collection('usuarios').document(user_id).collection('comentarios').document(sentence.id)
            batch.update(doc_ref, sentence_data)

        batch.commit()
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


###########
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

        # # Recorrer los documentos y agruparlos por mes y año
        # for doc in query:
        #     fecha = doc.get('fecha')  # Obtener el objeto Timestamp directamente
            
        #     # Obtener el año y mes de la fecha
        #     anio = fecha.year
        #     mes = fecha.month
            
        #     # Agrupar los comentarios por mes y año
        #     if anio not in comentarios_agrupados:
        #         comentarios_agrupados[anio] = {}
            
        #     if mes not in comentarios_agrupados[anio]:
        #         comentarios_agrupados[anio][mes] = []
            
        #     comentarios_agrupados[anio][mes].append(doc.to_dict())
            
        # # Calcular el número de veces que se repite cada categoría (0, 1, 2) en cada mes
        # for anio, meses in comentarios_agrupados.items():
        #     for mes, comentarios in meses.items():
        #         categorias_count = [0, 0, 0]
        #         for comentario in comentarios:
        #             categoria = comentario.get('categoria')
        #             categorias_count[categoria] += 1
        #         comentarios_agrupados[anio][mes].append((('cantCategoria', categorias_count),('anio', anio),('mes', mes)))


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
            
        # Calcular el número de veces que se repite cada categoría (0, 1, 2) en cada mes
        for anio, meses in comentarios_agrupados.items():
            for mes, comentarios in meses.items():
                categorias_count = [0, 0, 0]
                for comentario in comentarios:
                    categoria = comentario.get('categoria')
                    categorias_count[categoria] += 1
                comentarios_agrupados[anio][mes].append((('cantCategoria', categorias_count),('anio', anio),('mes', mes)))
