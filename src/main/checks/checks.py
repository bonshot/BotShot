"""
Módulo que contiene funciones que verifican
condiciones.
"""

from discord import Message

from ..db.atajos import existe_canal_escuchado


def es_canal_escuchado(mensaje: Message) -> bool:
    """
    Devuelve 'True' si se está en un canal escuchado.
    Si no, devuelve 'False'.
    """
    if mensaje.guild is None: # Si es un mensaje enviado por slash commands, por ejemplo
        return False

    return existe_canal_escuchado(id_canal=mensaje.channel.id)


def mensaje_tiene_imagen(mensaje: Message) -> bool:
    """
    Devuelve 'True' si el mensaje contiene una imagen.
    Caso contrario, devuelve 'False'.
    """
    if not mensaje.attachments:
        return False

    for contenido in mensaje.attachments:
        if (contenido.content_type is not None
            and "image" not in contenido.content_type):
            return False

    return True
