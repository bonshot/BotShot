"""
Módulo que contiene funciones que verifican
condiciones.
"""

from discord import Message

from archivos import cargar_json
from constantes import PROPERTIES_FILE

def es_canal_escuchado(mensaje: Message):
    """
    Devuelve 'True' si se está en un canal escuchado.
    Si no, devuelve 'False'.
    """
    canal_actual = str(mensaje.channel.id)
    dic_propiedades = cargar_json(PROPERTIES_FILE)
    return canal_actual in dic_propiedades['canales_escuchables']

def mensaje_tiene_imagen(mensaje: Message):
    """
    Devuelve 'True' si el mensaje contiene una imagen.
    Caso contrario, devuelve 'False'.
    """
    if not mensaje.attachments: 
        return False

    for contenido in mensaje.attachments:
        if "image" not in contenido.content_type:
            return False

    return True