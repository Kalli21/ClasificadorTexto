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
        
        result = tf.sigmoid(self.model(tf.constant(texts)))
        return result