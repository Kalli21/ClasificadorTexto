from math import ceil
import os
import shutil

import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text
import pandas as pd

class clasificacion_text:
    def __init__(self):
        self.model = tf.saved_model.load("Models_IA/algoritmo_DL/text_clasificador_bert")
        
    def predecir_text(self,texts):        
        # result = tf.sigmoid(self.model(tf.constant(texts)))
        # return result
        MAX_BATCH_SIZE = 200  # Tamaño máximo del lote

        # Dividir la lista de comentarios en lotes más pequeños
        num_batches = ceil(len(texts) / MAX_BATCH_SIZE)
        batches = [texts[i:i+MAX_BATCH_SIZE] for i in range(0, len(texts), MAX_BATCH_SIZE)]

        results = []

        for batch in batches:
            result = tf.sigmoid(self.model(tf.constant(batch)))
            results.extend(result.numpy().tolist())

        return results