"""
Módulo para atajos de INSERT.
"""

from io import BytesIO
from sqlite3 import connect
from typing import Optional

from ..database import (DEFAULT_DB, actualizar_dato_de_tabla,
                        existe_dato_en_tabla, insertar_datos_en_tabla)
from .actualizar_db import (actualizar_emoji_de_jugador,
                            actualizar_foto_perfil_de_jugador,
                            actualizar_nombre_de_jugador)
from .consulta_db import existe_canal_escuchado, existe_jugador_registrado
from .sacar_db import get_prefijo_default


def actualizar_guild(guild_id: int, nombre_guild: str) -> bool:
    """
    Registra el guild en la DB.

    Devuelve 'True' si el guild ya está presente, sino devuelve 'False'.
    """

    if existe_dato_en_tabla(tabla="guilds", id=guild_id):
        actualizar_dato_de_tabla(tabla="guilds",
                                 nombre_col="nombre",
                                 valor=nombre_guild,
                                 # condiciones,
                                 id=guild_id)
        return True

    insertar_datos_en_tabla(tabla="guilds",
                            llave_primaria_por_defecto=False,
                            valores=(guild_id, nombre_guild))
    actualizar_prefijo(get_prefijo_default(), guild_id)
    return False


def actualizar_prefijo(nuevo_prefijo: str, guild_id: int) -> bool:
    """
    Actualiza el prefijo de un guild específico.

    Devuelve 'True' si el prefijo ya está presente, sino devuelve 'False'.
    """

    if existe_dato_en_tabla(tabla="prefijos", id_guild=guild_id):
        actualizar_dato_de_tabla(tabla="prefijos",
                                 nombre_col="prefijo",
                                 valor=nuevo_prefijo)
        return True

    insertar_datos_en_tabla(tabla="prefijos",
                            llave_primaria_por_defecto=True,
                            valores=(guild_id, nuevo_prefijo))
    return False


def actualizar_canal_escuchado(id_canal: int, nombre_canal: str, id_guild: int) -> bool:
    """
    Actualiza los datos de canales escuchables.

    Devuelve 'True' si el canal ya está presente, sino devuelve 'False'.
    """

    if existe_canal_escuchado(id_canal=id_canal):
        actualizar_dato_de_tabla(tabla="canales_escuchables",
                                    nombre_col="nombre",
                                    valor=nombre_canal,
                                    # condiciones
                                    id=id_canal)
        return True

    insertar_datos_en_tabla(tabla="canales_escuchables",
                            llave_primaria_por_defecto=False,
                            valores=(id_canal, id_guild, nombre_canal))
    return False


def insertar_recomendacion_carpeta(nombre_carpeta: str,
                                   nombre_usuario: str,
                                   id_usuario: int) -> bool:
    """
    Inserta una recomendación hecha por un usuario.

    Devuelve 'True' si dicha recomendación no es repetida,
    caso contrario devuelve 'False'.
    """

    if existe_dato_en_tabla(tabla="carpetas_recomendadas",
                            recomendacion=nombre_carpeta,
                            id_usuario=id_usuario):
        return False

    insertar_datos_en_tabla(tabla="carpetas_recomendadas",
                            llave_primaria_por_defecto=True,
                            valores=(nombre_carpeta, nombre_usuario, id_usuario))
    return True


def registrar_usuario_autorizado(nombre: str,
                                 discriminador: str,
                                 id_usuario: int) -> bool:
    """
    Registra un usuario entre los autorizados.

    Si el usuario no está repetido, devuelve 'True', sino
    devuelve 'False'.
    """

    if existe_dato_en_tabla(tabla="usuarios_autorizados",
                            id=id_usuario):
        return False

    insertar_datos_en_tabla(tabla="usuarios_autorizados",
                            llave_primaria_por_defecto=False,
                            valores=(id_usuario, nombre, discriminador))
    return True


def registrar_jugador(id_jugador: str,
                      nombre: str,
                      emoji: Optional[str]=None,
                      foto_perfil: Optional[BytesIO]=None) -> bool:
    """
    Registra un jugador en la DB.

    Si el jugador ya existe devuelve `False` y trata de actualizarlo;
    sino devuelve `True`.
    """

    emoji_val = (emoji if emoji is not None else " ")
    img_val = (BytesIO(b"\x00") if foto_perfil is None else foto_perfil)
    img_val.seek(0)

    if existe_jugador_registrado(id_jugador):
        actualizar_nombre_de_jugador(id_jugador=id_jugador,
                                     nuevo_nombre=nombre)
        actualizar_emoji_de_jugador(id_jugador=id_jugador,
                                    nuevo_emoji=emoji_val)
        actualizar_foto_perfil_de_jugador(id_jugador=id_jugador,
                                          nueva_imagen=img_val)
        
        return False

    datos = {
        "id": id_jugador,
        "nombre": nombre,
        "emoji": emoji_val,
        "img": img_val.read()
    }
    with connect(DEFAULT_DB) as con:
        cur = con.cursor()
        cur.execute("INSERT INTO jugadores VALUES(:id, :nombre, :emoji, :img)", datos)

    return True
