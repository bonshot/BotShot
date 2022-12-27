"""
Módulo para atajos de comandos DELETE.
"""

from ..database import borrar_datos_de_tabla


def borrar_canal_escuchado(canal_id: int) -> None:
    """
    Borra un canal de los escuchados de BotShot.
    """

    borrar_datos_de_tabla(tabla="canales_escuchables",
                          id=canal_id)


def borrar_recomendacion_carpeta(nombre_carpeta: str) -> None:
    """
    Borra una recomendacion de las que ya hay hechas.
    """

    borrar_datos_de_tabla(tabla="carpetas_recomendadas",
                          recomendacion=nombre_carpeta)


def borrar_usuario_autorizado(id_usuario: int) -> None:
    """
    Elimina la autorización de un usuario de la DB.
    """

    borrar_datos_de_tabla(tabla="usuarios_autorizados",
                          id=id_usuario)
