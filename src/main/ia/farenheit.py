import tensorflow as tf
import numpy as np
import time

# Clase para obtener el tiempo total de entrenamiento
class TiempoEntrenamiento(tf.keras.callbacks.Callback):
    def on_train_begin(self, logs={}):
        self.tiempo_entrenamiento = 0

    def on_epoch_begin(self, batch, logs={}):
        self.tiempo_entrenamiento = time.time()

    def on_epoch_end(self, batch, logs={}):
        self.tiempo_entrenamiento = time.time() - self.tiempo_entrenamiento

# Datos de entrenamiento
celsius = np.array([-40, -10, 0, 8, 15, 22, 38], dtype=float)
fahrenheit = np.array([-40, 14, 32, 46, 59, 72, 100], dtype=float)

# Capa de entrada
capa_entrada = tf.keras.layers.Input(shape=(1,))

# Capa oculta
capa_oculta = tf.keras.layers.Dense(units=4, activation='relu')(capa_entrada) # 4 neuronas, función de activación relu porque se trata de una regresión

# Capa de salida
capa_salida = tf.keras.layers.Dense(units=1)(capa_oculta) 

# Modelo
modelo = tf.keras.Model(inputs=capa_entrada, outputs=capa_salida)

# Compilación del modelo
modelo.compile(loss='mean_squared_error', optimizer=tf.keras.optimizers.Adam(0.1))

def convertir_celsius_a_fahrenheit(celsius_asked: float, iteraciones: int):
    callback_tiempo_entrenamiento = TiempoEntrenamiento()
    modelo.fit(celsius, fahrenheit, epochs = iteraciones, verbose=False, callbacks = [callback_tiempo_entrenamiento]) # epochs: número de iteraciones, verbose: muestra el progreso del entrenamiento
    return callback_tiempo_entrenamiento.tiempo_entrenamiento, modelo.predict([celsius_asked])
