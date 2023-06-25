"""
Módulo para atajos de UPDATE.
"""

from io import BytesIO
from sqlite3 import connect

from ..database import DEFAULT_DB, actualizar_dato_de_tabla


def actualizar_nombre_de_jugador(id_jugador: str, nuevo_nombre: str) -> None:
    """
    Cambia el nombre de un jugador en la DB por otro más nuevo.
    """

    actualizar_dato_de_tabla(tabla="jugadores",
                             nombre_col="nombre",
                             valor=nuevo_nombre,
                             # condiciones,
                             id=id_jugador)


def actualizar_emoji_de_jugador(id_jugador: str, nuevo_emoji: str) -> None:
    """
    Cambia el emoji de un jugador en la DB por otro más nuevo.

    Se espera que el emoji venga en el formato 'U+XXXX'.
    """

    actualizar_dato_de_tabla(tabla="jugadores",
                             nombre_col="emoji",
                             valor=nuevo_emoji,
                             # condiciones,
                             id=id_jugador)


def actualizar_foto_perfil_de_jugador(id_jugador: str, nueva_imagen: BytesIO) -> None:
    """
    Cambia la imagen de perfil de un jugador en la DB por otra.
    """

    datos = {
        "idjug": id_jugador,
        "img": nueva_imagen.read()
    }

    with connect(DEFAULT_DB) as con:
        cur = con.cursor()
        cur.execute("UPDATE jugadores SET img=:img WHERE id=:idjug;", datos)
