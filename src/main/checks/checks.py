"""
Módulo que contiene funciones que verifican
condiciones.
"""

from discord import Message

from ..archivos import cargar_json
from ..constantes import PROPERTIES_FILE


def es_canal_escuchado(mensaje: Message) -> bool:
    """
    Devuelve 'True' si se está en un canal escuchado.
    Si no, devuelve 'False'.
    """
    if mensaje.guild is None: # Si es un mensaje enviado por slash commands, por ejemplo
        return False
    guild_actual = str(mensaje.guild.id)
    canal_actual = str(mensaje.channel.id)
    dic_propiedades = cargar_json(PROPERTIES_FILE)
    return (guild_actual in dic_propiedades['canales_escuchables']
            and canal_actual in dic_propiedades['canales_escuchables'][guild_actual])


def mensaje_tiene_imagen(mensaje: Message) -> bool:
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
